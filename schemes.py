#============================================================
#  schemes.py  —  Welfare Scheme Database
#  Source: MyScheme.gov.in  |  NSS IIT Roorkee Open Projects 2026
#  10 high-impact schemes for rural India
# ============================================================

SCHEMES = [
    {
        "id": "PM_KISAN",
        "name": "PM-KISAN (Pradhan Mantri Kisan Samman Nidhi)",
        "name_hindi": "पीएम-किसान योजना",
        "description": "₹6,000/year direct income support to farmer families in 3 installments of ₹2,000 each",
        "description_hindi": "किसान परिवारों को साल में ₹6,000 — तीन किस्तों में सीधे बैंक खाते में",
        "eligibility": {
            "occupation": ["farmer"],
            "land": True,
            "income_limit": None
        },
        "documents": [
            "Aadhaar Card",
            "Bank Passbook (with IFSC)",
            "Land Records / Khatoni",
            "Mobile Number linked to Aadhaar"
        ],
        "documents_hindi": [
            "आधार कार्ड",
            "बैंक पासबुक (IFSC के साथ)",
            "जमीन के कागज / खतौनी",
            "आधार से जुड़ा मोबाइल नंबर"
        ],
        "apply_at": "Local Patwari / CSC Center / pmkisan.gov.in",
        "benefit_amount": 6000,
        "scheme_url": "https://pmkisan.gov.in"
    },
    {
        "id": "AYUSHMAN",
        "name": "Ayushman Bharat - PMJAY",
        "name_hindi": "आयुष्मान भारत योजना",
        "description": "Free health insurance up to ₹5 lakh/year per family at 25,000+ empanelled hospitals",
        "description_hindi": "सरकारी और प्राइवेट अस्पतालों में ₹5 लाख तक का मुफ्त इलाज हर साल",
        "eligibility": {
            "occupation": ["farmer", "labor", "gig_worker", "unemployed"],
            "income_limit": 200000
        },
        "documents": [
            "Aadhaar Card",
            "Ration Card",
            "Income Certificate"
        ],
        "documents_hindi": [
            "आधार कार्ड",
            "राशन कार्ड",
            "आय प्रमाण पत्र"
        ],
        "apply_at": "Nearest govt hospital / CSC / pmjay.gov.in",
        "benefit_amount": 500000,
        "scheme_url": "https://pmjay.gov.in"
    },
    {
        "id": "PMAY",
        "name": "Pradhan Mantri Awas Yojana Gramin (PMAY-G)",
        "name_hindi": "प्रधानमंत्री आवास योजना (ग्रामीण)",
        "description": "Financial assistance of ₹1.2–1.3 lakh to build a pucca house for homeless rural families",
        "description_hindi": "पक्का मकान बनाने के लिए ₹1.20–1.30 लाख की सहायता",
        "eligibility": {
            "occupation": ["farmer", "labor", "unemployed"],
            "has_house": False,
            "income_limit": 300000
        },
        "documents": [
            "Aadhaar Card",
            "Bank Passbook",
            "BPL / SECC Certificate",
            "Land Ownership Proof"
        ],
        "documents_hindi": [
            "आधार कार्ड",
            "बैंक पासबुक",
            "BPL / SECC प्रमाण पत्र",
            "जमीन के स्वामित्व के कागज"
        ],
        "apply_at": "Gram Panchayat / Block Development Office",
        "benefit_amount": 130000,
        "scheme_url": "https://pmayg.nic.in"
    },
    {
        "id": "UJJWALA",
        "name": "Pradhan Mantri Ujjwala Yojana (PMUY)",
        "name_hindi": "उज्ज्वला योजना",
        "description": "Free LPG gas connection to women from BPL/SECC households",
        "description_hindi": "BPL परिवार की महिलाओं को मुफ्त गैस कनेक्शन",
        "eligibility": {
            "gender": ["female"],
            "occupation": ["farmer", "labor", "unemployed"],
            "income_limit": 100000,
            "bpl": True
        },
        "documents": [
            "Aadhaar Card",
            "BPL Ration Card",
            "Bank Passbook",
            "Passport Size Photo"
        ],
        "documents_hindi": [
            "आधार कार्ड",
            "BPL राशन कार्ड",
            "बैंक पासबुक",
            "पासपोर्ट साइज फोटो"
        ],
        "apply_at": "Nearest LPG distributor / CSC center",
        "benefit_amount": 1600,
        "scheme_url": "https://pmuy.gov.in"
    },
    {
        "id": "NREGA",
        "name": "MGNREGA (Mahatma Gandhi National Rural Employment Guarantee Act)",
        "name_hindi": "मनरेगा (महात्मा गांधी राष्ट्रीय ग्रामीण रोजगार गारंटी)",
        "description": "Guaranteed 100 days of paid wage employment per year to every rural household adult",
        "description_hindi": "हर ग्रामीण परिवार को साल में 100 दिन काम की कानूनी गारंटी",
        "eligibility": {
            "location": "rural",
            "occupation": ["farmer", "labor", "unemployed"]
        },
        "documents": [
            "Aadhaar Card",
            "Bank Passbook",
            "Job Card (obtained from Gram Panchayat)"
        ],
        "documents_hindi": [
            "आधार कार्ड",
            "बैंक पासबुक",
            "जॉब कार्ड (ग्राम पंचायत से बनवाएं)"
        ],
        "apply_at": "Gram Panchayat Office",
        "benefit_amount": None,
        "scheme_url": "https://nrega.nic.in"
    },
    {
        "id": "SUKANYA",
        "name": "Sukanya Samriddhi Yojana (SSY)",
        "name_hindi": "सुकन्या समृद्धि योजना",
        "description": "High-interest (~8.2%) tax-free savings scheme exclusively for girl child (below age 10)",
        "description_hindi": "बेटी (10 साल से कम) के लिए ~8.2% ब्याज वाली टैक्स-फ्री बचत योजना",
        "eligibility": {
            "has_girl_child": True,
            "girl_age_limit": 10
        },
        "documents": [
            "Girl Child's Birth Certificate",
            "Parent / Guardian Aadhaar Card",
            "Parent / Guardian PAN Card",
            "Passport Photo of Parent and Child"
        ],
        "documents_hindi": [
            "बच्ची का जन्म प्रमाण पत्र",
            "माता-पिता / अभिभावक का आधार",
            "माता-पिता / अभिभावक का पैन कार्ड",
            "माता-पिता और बच्ची की फोटो"
        ],
        "apply_at": "Post Office / Any nationalized bank branch",
        "benefit_amount": None,
        "scheme_url": "https://www.indiapost.gov.in"
    },
    {
        "id": "PMSBY",
        "name": "Pradhan Mantri Suraksha Bima Yojana (PMSBY)",
        "name_hindi": "पीएम सुरक्षा बीमा योजना",
        "description": "Accidental death/disability insurance of ₹2 lakh for just ₹20/year — auto-deducted from bank",
        "description_hindi": "सिर्फ ₹20/साल में ₹2 लाख का दुर्घटना बीमा — बैंक से अपने आप कटता है",
        "eligibility": {
            "age_min": 18,
            "age_max": 70,
            "has_bank_account": True
        },
        "documents": [
            "Aadhaar Card",
            "Bank Account (savings)"
        ],
        "documents_hindi": [
            "आधार कार्ड",
            "बचत बैंक खाता"
        ],
        "apply_at": "Your bank branch / net banking / bank app",
        "benefit_amount": 200000,
        "scheme_url": "https://jansuraksha.gov.in"
    },
    {
        "id": "PMJJBY",
        "name": "Pradhan Mantri Jeevan Jyoti Bima Yojana (PMJJBY)",
        "name_hindi": "पीएम जीवन ज्योति बीमा योजना",
        "description": "Life insurance cover of ₹2 lakh on death for just ₹436/year",
        "description_hindi": "सिर्फ ₹436/साल में ₹2 लाख का जीवन बीमा",
        "eligibility": {
            "age_min": 18,
            "age_max": 50,
            "has_bank_account": True
        },
        "documents": [
            "Aadhaar Card",
            "Bank Account (savings)"
        ],
        "documents_hindi": [
            "आधार कार्ड",
            "बचत बैंक खाता"
        ],
        "apply_at": "Your bank branch / net banking / bank app",
        "benefit_amount": 200000,
        "scheme_url": "https://jansuraksha.gov.in"
    },
    {
        "id": "E_SHRAM",
        "name": "e-Shram Card (Unorganised Workers National Database)",
        "name_hindi": "ई-श्रम कार्ड",
        "description": "National ID card for unorganised workers — unlocks priority access to 10+ welfare schemes",
        "description_hindi": "असंगठित मजदूरों के लिए राष्ट्रीय पहचान पत्र — 10+ योजनाओं का दरवाजा खुलता है",
        "eligibility": {
            "occupation": ["labor", "gig_worker", "farmer"],
            "age_min": 16,
            "age_max": 59,
            "not_epfo_member": True
        },
        "documents": [
            "Aadhaar Card",
            "Bank Passbook",
            "Mobile Number linked to Aadhaar"
        ],
        "documents_hindi": [
            "आधार कार्ड",
            "बैंक पासबुक",
            "आधार से जुड़ा मोबाइल नंबर"
        ],
        "apply_at": "eshram.gov.in / CSC Center / UMANG App",
        "benefit_amount": None,
        "scheme_url": "https://eshram.gov.in"
    },
    {
        "id": "MUDRA",
        "name": "PM MUDRA Yojana (Micro Units Development & Refinance Agency)",
        "name_hindi": "पीएम मुद्रा योजना",
        "description": "Collateral-free business loans from ₹10,000 (Shishu) up to ₹10 lakh (Tarun) for small businesses",
        "description_hindi": "बिना गारंटी के ₹10,000 से ₹10 लाख तक का व्यापार लोन — कोई गिरवी नहीं",
        "eligibility": {
            "occupation": ["gig_worker", "labor"],
            "has_business": True
        },
        "documents": [
            "Aadhaar Card",
            "PAN Card",
            "Business Proof / Address Proof of Business",
            "Bank Statement (last 6 months)",
            "2 Passport Photos"
        ],
        "documents_hindi": [
            "आधार कार्ड",
            "पैन कार्ड",
            "व्यापार का प्रमाण / दुकान का पता",
            "6 महीने की बैंक स्टेटमेंट",
            "2 पासपोर्ट फोटो"
        ],
        "apply_at": "Any bank / NBFC / mudra.org.in",
        "benefit_amount": 1000000,
        "scheme_url": "https://mudra.org.in"
    }
]


# ============================================================
#  Eligibility Matching Engine
#  Pure rule-based — NO LLM involved — prevents hallucination
# ============================================================

def find_eligible_schemes(user_profile):
    """
    Match user profile against scheme eligibility rules.
    Returns list of eligible scheme dicts.
    All logic is deterministic — never relies on AI.
    """
    eligible = []

    occupation  = user_profile.get("occupation", "")
    income      = user_profile.get("income", 999999)
    gender      = user_profile.get("gender", "male")
    has_land    = user_profile.get("has_land", False)
    has_house   = user_profile.get("has_house", True)
    has_girl    = user_profile.get("has_girl_child", False)
    has_bank    = user_profile.get("has_bank", True)
    age         = user_profile.get("age", 35)
    location    = user_profile.get("location", "rural")
    has_biz     = user_profile.get("has_business", False)

    for scheme in SCHEMES:
        e = scheme["eligibility"]
        match = True

        if "occupation" in e:
            if occupation not in e["occupation"]:
                match = False

        if match and "income_limit" in e and e["income_limit"] is not None:
            if income > e["income_limit"]:
                match = False

        if match and "gender" in e:
            if gender not in e["gender"]:
                match = False

        if match and e.get("land"):
            if not has_land:
                match = False

        if match and "has_house" in e and e["has_house"] is False:
            if has_house:      # scheme needs NO house; user HAS one
                match = False

        if match and e.get("has_girl_child"):
            if not has_girl:
                match = False

        if match and e.get("has_bank_account"):
            if not has_bank:
                match = False

        if match and "age_min" in e:
            if age < e["age_min"] or age > e.get("age_max", 999):
                match = False

        if match and "location" in e:
            if location != e["location"]:
                match = False

        if match and e.get("has_business"):
            if not has_biz:
                match = False

        if match:
            eligible.append(scheme)

    return eligible