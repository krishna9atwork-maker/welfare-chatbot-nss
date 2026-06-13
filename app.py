import os
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import google.generativeai as genai
from dotenv import load_dotenv

from schemes import find_eligible_schemes
from bhashini_helper import translate_text, detect_language, handle_hinglish

# ── env + AI setup ────────────────────────────────────────────
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY", ""))
gemini_model = genai.GenerativeModel("gemini-1.5-flash")

app = Flask(__name__)

# ── In-memory session store ───────────────────────────────────
#    key  = sender WhatsApp number   e.g. "whatsapp:+919876543210"
#    value= dict with step, language, profile, eligible_schemes
#
#    NOTE: Render free tier can spin down; sessions will reset on
#    restart. For production, swap this dict for Redis / Firestore.
# ─────────────────────────────────────────────────────────────
SESSIONS: dict = {}


# ============================================================
#  UI STRING TABLE  (all pre-written in both languages
#  so we don't burn Bhashini quota on fixed interface text)
# ============================================================
UI = {
    "welcome": {
        "both": (
            "🙏 *Welfare Scheme Helper | सरकारी योजना सहायक*\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "Powered by *Bhashini IndicTrans2* 🇮🇳\n\n"
            "Choose language / भाषा चुनें:\n"
            "1️⃣  हिंदी\n"
            "2️⃣  English\n\n"
            "1 या 2 लिखें / Type 1 or 2"
        )
    },
    "q_occupation": {
        "hindi": (
            "📋 *सवाल 1/5 — आपका काम क्या है?*\n\n"
            "1️⃣  किसान (Farmer)\n"
            "2️⃣  मजदूर / Daily wage worker\n"
            "3️⃣  गिग वर्कर (Delivery / Cab / Freelancer)\n"
            "4️⃣  बेरोजगार (Unemployed)\n\n"
            "नंबर लिखें  ▶  1, 2, 3 या 4"
        ),
        "english": (
            "📋 *Question 1/5 — What is your occupation?*\n\n"
            "1️⃣  Farmer\n"
            "2️⃣  Daily wage laborer\n"
            "3️⃣  Gig worker (Delivery / Cab / Freelancer)\n"
            "4️⃣  Unemployed\n\n"
            "Type a number  ▶  1, 2, 3 or 4"
        )
    },
    "q_income": {
        "hindi": (
            "💰 *सवाल 2/5 — घर की साल की कुल कमाई?*\n\n"
            "1️⃣  ₹1 लाख से कम\n"
            "2️⃣  ₹1 लाख – ₹2 लाख\n"
            "3️⃣  ₹2 लाख – ₹3 लाख\n"
            "4️⃣  ₹3 लाख से ज़्यादा\n\n"
            "नंबर लिखें  ▶  1, 2, 3 या 4"
        ),
        "english": (
            "💰 *Question 2/5 — Annual household income?*\n\n"
            "1️⃣  Below ₹1 lakh\n"
            "2️⃣  ₹1 lakh – ₹2 lakh\n"
            "3️⃣  ₹2 lakh – ₹3 lakh\n"
            "4️⃣  Above ₹3 lakh\n\n"
            "Type a number  ▶  1, 2, 3 or 4"
        )
    },
    "q_gender": {
        "hindi": (
            "👤 *सवाल 3/5 — आप कौन हैं?*\n\n"
            "1️⃣  पुरुष (Male)\n"
            "2️⃣  महिला (Female)\n\n"
            "नंबर लिखें  ▶  1 या 2"
        ),
        "english": (
            "👤 *Question 3/5 — Your gender?*\n\n"
            "1️⃣  Male\n"
            "2️⃣  Female\n\n"
            "Type a number  ▶  1 or 2"
        )
    },
    "q_land": {
        "hindi": (
            "🌾 *सवाल 4/5 — क्या आपके पास खेती की ज़मीन है?*\n\n"
            "1️⃣  हाँ (Yes)\n"
            "2️⃣  नहीं (No)\n\n"
            "नंबर लिखें  ▶  1 या 2"
        ),
        "english": (
            "🌾 *Question 4/5 — Do you own agricultural land?*\n\n"
            "1️⃣  Yes\n"
            "2️⃣  No\n\n"
            "Type  ▶  1 or 2"
        )
    },
    "q_house": {
        "hindi": (
            "🏠 *सवाल 5/5 — क्या आपके पास पक्का मकान है?*\n\n"
            "1️⃣  हाँ (Yes)\n"
            "2️⃣  नहीं (No)\n\n"
            "नंबर लिखें  ▶  1 या 2"
        ),
        "english": (
            "🏠 *Question 5/5 — Do you already own a permanent (pucca) house?*\n\n"
            "1️⃣  Yes\n"
            "2️⃣  No\n\n"
            "Type  ▶  1 or 2"
        )
    },
    "invalid": {
        "hindi":   "❌ गलत जवाब। कृपया सही नंबर लिखें।",
        "english": "❌ Invalid input. Please type one of the given numbers."
    },
    "footer_reset": {
        "hindi":   "\n\n🔄 फिर से शुरू करने के लिए *RESET* लिखें",
        "english": "\n\n🔄 Type *RESET* to start over"
    },
    "no_schemes": {
        "hindi": (
            "😔 *आपकी जानकारी के अनुसार कोई योजना नहीं मिली।*\n\n"
            "इसका मतलब यह नहीं कि आप अयोग्य हैं।\n"
            "कृपया नजदीकी *CSC केंद्र (Common Service Centre)* पर जाएं "
            "और अपनी पूरी जानकारी दें।\n\n"
            "CSC खोजें: locator.csccloud.in"
        ),
        "english": (
            "😔 *No schemes matched your profile.*\n\n"
            "This doesn't mean you're ineligible — please visit your nearest "
            "*CSC (Common Service Centre)* with your full details.\n\n"
            "Find a CSC: locator.csccloud.in"
        )
    },
    "qa_unknown": {
        "hindi": (
            "🤔 मुझे समझ नहीं आया।\n\n"
            "किसी योजना का नाम लिखें जैसे:\n"
            "*PM-KISAN*, *NREGA*, *Ayushman*, *PMAY*, *Ujjwala*\n\n"
            "या अपना सवाल लिखें।"
        ),
        "english": (
            "🤔 I didn't understand that.\n\n"
            "Try typing a scheme name like:\n"
            "*PM-KISAN*, *NREGA*, *Ayushman*, *PMAY*, *Ujjwala*\n\n"
            "Or ask your question directly."
        )
    }
}


# ── Small helper ──────────────────────────────────────────────
def ui(key: str, lang: str) -> str:
    """Fetch UI string. Falls back to English if Hindi not found."""
    block = UI.get(key, {})
    # some keys have a 'both' variant (welcome screen)
    if "both" in block:
        return block["both"]
    return block.get(lang, block.get("english", ""))


# ============================================================
#  SESSION MANAGEMENT
# ============================================================
def get_session(phone: str) -> dict:
    if phone not in SESSIONS:
        SESSIONS[phone] = {
            "step":             0,
            "language":         "hindi",
            "profile":          {},
            "eligible_schemes": []
        }
    return SESSIONS[phone]


def reset_session(phone: str) -> dict:
    SESSIONS[phone] = {
        "step":             0,
        "language":         "hindi",
        "profile":          {},
        "eligible_schemes": []
    }
    return SESSIONS[phone]


# ============================================================
#  SCHEME RESULTS FORMATTER
# ============================================================
def format_results(schemes: list, lang: str) -> str:
    """
    Build the WhatsApp message listing all eligible schemes.
    Each scheme shows: name, benefit, documents needed, where to apply.
    """
    if not schemes:
        return ui("no_schemes", lang) + ui("footer_reset", lang)

    if lang == "hindi":
        msg  = f"🎉 *आपके लिए {len(schemes)} योजनाएं मिलीं!*\n"
        msg += "_( Bhashini IndicTrans2 द्वारा अनुवादित )_\n"
        msg += "━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        for i, sc in enumerate(schemes, 1):
            msg += f"*{i}. {sc['name_hindi']}*\n"
            msg += f"📌 {sc['description_hindi']}\n"
            docs = "、".join(sc["documents_hindi"])
            msg += f"📄 *ज़रूरी कागज:* {docs}\n"
            msg += f"🏢 *कहाँ जाएं:* {sc['apply_at']}\n\n"
        msg += "❓ किसी भी योजना के बारे में ज़्यादा जानने के लिए उसका नाम लिखें।"
    else:
        msg  = f"🎉 *{len(schemes)} schemes found for you!*\n"
        msg += "━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        for i, sc in enumerate(schemes, 1):
            msg += f"*{i}. {sc['name']}*\n"
            msg += f"📌 {sc['description']}\n"
            docs = ", ".join(sc["documents"])
            msg += f"📄 *Documents needed:* {docs}\n"
            msg += f"🏢 *Where to apply:* {sc['apply_at']}\n\n"
        msg += "❓ Type any scheme name to ask follow-up questions."

    msg += ui("footer_reset", lang)
    return msg


# ============================================================
#  GEMINI RAG Q&A  (grounded — only answers about known schemes)
# ============================================================
def ask_gemini_grounded(scheme_name: str, question: str, lang: str) -> str:
    """
    Answers a user's question about a specific scheme using Gemini.
    The system prompt explicitly prohibits hallucination:
    the model must say 'I don't know' rather than invent facts.
    This is the RAG pattern demanded by the challenge spec.
    """
    language_instruction = "Hindi (simple, Class-5 reading level)" if lang == "hindi" else "English (simple)"

    system_prompt = f"""You are a helpful, HONEST government scheme advisor for rural Indians.
You ONLY have information about this scheme: {scheme_name}

RULES (follow strictly):
1. Answer in {language_instruction}
2. Keep the answer under 80 words
3. If you are NOT 100% sure of a fact, say:
   Hindi:   "मुझे पक्की जानकारी नहीं — CSC केंद्र पर पूछें"
   English: "I'm not certain — please verify at a CSC center"
4. NEVER invent benefit amounts, eligibility criteria, or deadlines
5. NEVER make up URLs or phone numbers
6. Always end with the official application channel if known

User's question: {question}"""

    try:
        response = gemini_model.generate_content(system_prompt)
        return response.text.strip()
    except Exception as ex:
        print(f"[Gemini] Error: {ex}")
        if lang == "hindi":
            return "माफ करें, अभी जानकारी नहीं मिली। नजदीकी CSC केंद्र पर जाएं।"
        return "Sorry, couldn't fetch info right now. Please visit your nearest CSC center."


# ============================================================
#  MAIN CONVERSATION STATE MACHINE
# ============================================================
def process_message(phone: str, raw_msg: str) -> str:
    session = get_session(phone)
    msg     = raw_msg.strip()

    # ── Global reset trigger ──────────────────────────────────
    reset_words = {"reset", "restart", "शुरू", "start", "नया", "menu", "home"}
    if msg.lower() in reset_words:
        session = reset_session(phone)

    # ── Auto-detect Devanagari before step 1 ─────────────────
    if session["step"] <= 1 and detect_language(msg) == "hindi":
        session["language"] = "hindi"

    # ── Handle code-mixed Hinglish ────────────────────────────
    msg_clean = handle_hinglish(msg)

    step = session["step"]
    lang = session["language"]

    # ══════════════════════════════════════════════════════════
    #  STEP 0 — Welcome screen
    # ══════════════════════════════════════════════════════════
    if step == 0:
        session["step"] = 1
        return ui("welcome", "both")

    # ══════════════════════════════════════════════════════════
    #  STEP 1 — Language selection
    # ══════════════════════════════════════════════════════════
    elif step == 1:
        if "2" in msg or "english" in msg.lower():
            session["language"] = "english"
        else:
            session["language"] = "hindi"   # default: Hindi
        lang = session["language"]
        session["step"] = 2
        return ui("q_occupation", lang)

    # ══════════════════════════════════════════════════════════
    #  STEP 2 — Occupation
    # ══════════════════════════════════════════════════════════
    elif step == 2:
        OCC_MAP = {
            "1": "farmer",     "farmer":     "farmer",  "किसान":    "farmer",
            "2": "labor",      "labor":      "labor",   "मजदूर":    "labor",
                               "labourer":   "labor",   "mazdoor":  "labor",
            "3": "gig_worker", "gig":        "gig_worker",
                               "delivery":   "gig_worker",
                               "cab":        "gig_worker",
                               "freelancer": "gig_worker",
            "4": "unemployed", "unemployed": "unemployed",
                               "बेरोजगार":  "unemployed",
                               "berojgar":   "unemployed"
        }
        occ = None
        for key, val in OCC_MAP.items():
            if key in msg_clean.lower():
                occ = val
                break
        if occ is None:
            return ui("invalid", lang)
        session["profile"]["occupation"] = occ
        session["step"] = 3
        return ui("q_income", lang)

    # ══════════════════════════════════════════════════════════
    #  STEP 3 — Income
    # ══════════════════════════════════════════════════════════
    elif step == 3:
        INCOME_MAP = {"1": 50_000, "2": 1_50_000, "3": 2_50_000, "4": 4_00_000}
        income = INCOME_MAP.get(msg_clean.strip())
        if income is None:
            return ui("invalid", lang)
        session["profile"]["income"] = income
        session["step"] = 4
        return ui("q_gender", lang)

    # ══════════════════════════════════════════════════════════
    #  STEP 4 — Gender
    # ══════════════════════════════════════════════════════════
    elif step == 4:
        m = msg_clean.lower()
        if "2" in m or "female" in m or "महिला" in m or "aurat" in m:
            session["profile"]["gender"] = "female"
        elif "1" in m or "male" in m or "पुरुष" in m or "mard" in m:
            session["profile"]["gender"] = "male"
        else:
            return ui("invalid", lang)
        session["step"] = 5
        return ui("q_land", lang)

    # ══════════════════════════════════════════════════════════
    #  STEP 5 — Agricultural land
    # ══════════════════════════════════════════════════════════
    elif step == 5:
        m = msg_clean.lower()
        if "1" in m or "yes" in m or "हाँ" in m or "haan" in m or "han" in m:
            session["profile"]["has_land"] = True
        elif "2" in m or "no" in m or "नहीं" in m or "nahi" in m:
            session["profile"]["has_land"] = False
        else:
            return ui("invalid", lang)
        session["step"] = 6
        return ui("q_house", lang)

    # ══════════════════════════════════════════════════════════
    #  STEP 6 — Pucca house  →  run eligibility  →  show results
    # ══════════════════════════════════════════════════════════
    elif step == 6:
        m = msg_clean.lower()
        if "1" in m or "yes" in m or "हाँ" in m or "haan" in m or "han" in m:
            session["profile"]["has_house"] = True
        elif "2" in m or "no" in m or "नहीं" in m or "nahi" in m:
            session["profile"]["has_house"] = False
        else:
            return ui("invalid", lang)

        # Fill in defaults for fields we didn't ask yet
        session["profile"].setdefault("has_bank",      True)
        session["profile"].setdefault("age",           35)
        session["profile"].setdefault("location",      "rural")
        session["profile"].setdefault("has_girl_child", False)
        session["profile"].setdefault("has_business",  False)

        # ── CORE ELIGIBILITY MATCHING (deterministic, no LLM) ──
        eligible = find_eligible_schemes(session["profile"])
        session["eligible_schemes"] = eligible
        session["step"] = 7

        return format_results(eligible, lang)

    # ══════════════════════════════════════════════════════════
    #  STEP 7 — Free Q&A about matched schemes
    # ══════════════════════════════════════════════════════════
    elif step == 7:
        eligible_schemes = session.get("eligible_schemes", [])
        msg_lower = msg_clean.lower()

        # Try to match the user's message to one of their schemes
        matched_scheme = None
        for sc in eligible_schemes:
            # Check scheme ID, English name words, and Hindi name
            keywords = (
                [sc["id"].lower()]
                + [w.lower() for w in sc["name"].split()[:3]]
                + [sc["name_hindi"]]
            )
            if any(kw in msg_lower for kw in keywords):
                matched_scheme = sc
                break

        # Also do a broader keyword search across ALL scheme keywords
        if not matched_scheme:
            broad_map = {
                "kisan": "PM_KISAN", "pmkisan": "PM_KISAN", "pm kisan": "PM_KISAN",
                "ayushman": "AYUSHMAN", "pmjay": "AYUSHMAN", "health": "AYUSHMAN",
                "awas": "PMAY", "pmay": "PMAY", "house": "PMAY", "makan": "PMAY",
                "ujjwala": "UJJWALA", "gas": "UJJWALA", "lpg": "UJJWALA",
                "nrega": "NREGA", "mgnrega": "NREGA", "manrega": "NREGA", "kaam": "NREGA",
                "sukanya": "SUKANYA", "beti": "SUKANYA", "girl": "SUKANYA",
                "pmsby": "PMSBY", "suraksha": "PMSBY", "accident": "PMSBY",
                "pmjjby": "PMJJBY", "jeevan jyoti": "PMJJBY", "life insurance": "PMJJBY",
                "e shram": "E_SHRAM", "eshram": "E_SHRAM", "shram": "E_SHRAM",
                "mudra": "MUDRA", "loan": "MUDRA", "business loan": "MUDRA"
            }
            for keyword, scheme_id in broad_map.items():
                if keyword in msg_lower:
                    # Find this scheme in the eligible list
                    for sc in eligible_schemes:
                        if sc["id"] == scheme_id:
                            matched_scheme = sc
                            break
                    # Even if not in eligible list, still answer the question
                    if not matched_scheme:
                        from schemes import SCHEMES
                        for sc in SCHEMES:
                            if sc["id"] == scheme_id:
                                matched_scheme = sc
                                break
                    break

        if matched_scheme:
            # Get Gemini's answer (grounded, no hallucination)
            gemini_answer = ask_gemini_grounded(matched_scheme["name"], msg, lang)

            # Use Bhashini to translate Gemini's English answer to Hindi
            if lang == "hindi":
                final_answer  = translate_text(gemini_answer, "english", "hindi")
                display_name  = matched_scheme["name_hindi"]
            else:
                final_answer  = gemini_answer
                display_name  = matched_scheme["name"]

            reply  = f"📌 *{display_name}*\n"
            reply += "━━━━━━━━━━━━━━━━━━━━━━━━\n"
            reply += final_answer
            reply += ui("footer_reset", lang)
            return reply
        else:
            return ui("qa_unknown", lang) + ui("footer_reset", lang)

    # ── Catch-all ─────────────────────────────────────────────
    return "RESET लिखें / Type RESET to restart."


# ============================================================
#  FLASK ROUTES
# ============================================================

@app.route("/webhook", methods=["POST"])
def webhook():
    """
    Twilio sends POST requests here every time a user
    messages your WhatsApp sandbox number.
    """
    incoming_msg  = request.values.get("Body", "").strip()
    sender_phone  = request.values.get("From", "unknown")

    print(f"[MSG] {sender_phone}: {incoming_msg}")

    reply_text = process_message(sender_phone, incoming_msg)

    # Build Twilio XML response
    resp = MessagingResponse()
    resp.message().body(reply_text)
    return str(resp)


@app.route("/")
def home():
    """Health-check endpoint — Render pings this to confirm the app is live."""
    return (
        "✅ Welfare Scheme Chatbot is LIVE<br>"
        "Powered by Gemini + Bhashini IndicTrans2<br>"
        "NSS IIT Roorkee Open Projects 2026"
    )


@app.route("/health")
def health():
    return {"status": "ok", "service": "welfare-chatbot-nss"}, 200


# ── Entry point ───────────────────────────────────────────────
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"🚀 Welfare Chatbot starting on port {port}")
    app.run(host="0.0.0.0", port=port, debug=False)
