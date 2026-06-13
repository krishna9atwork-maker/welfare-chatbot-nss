

import requests
import os
from dotenv import load_dotenv

load_dotenv()

BHASHINI_USER_ID  = os.getenv("BHASHINI_USER_ID", "")
BHASHINI_API_KEY  = os.getenv("BHASHINI_API_KEY", "")

# Bhashini language code map
LANG_CODES = {
    "hindi":   "hi",
    "english": "en",
    "tamil":   "ta",
    "bengali": "bn",
    "marathi": "mr",
    "telugu":  "te",
    "kannada": "kn",
    "gujarati":"gu",
    "punjabi": "pa",
    "odia":    "or"
}

# Pipeline IDs (from Bhashini ULCA)
PIPELINE_ID = "64392f96daac500b55c543cd"   # IndicTrans2 pipeline


# ──────────────────────────────────────────────────────────────
#  STEP 1 of Bhashini two-step API: discover which model to use
# ──────────────────────────────────────────────────────────────
def _get_pipeline_config(src_lang: str, tgt_lang: str) -> dict | None:
    """
    Calls Bhashini Pipeline Search API.
    Returns the pipeline config dict, or None on failure.
    """
    url = "https://meity-auth.ulcacontrib.org/ulca/apis/v0/model/getModelsPipeline"

    payload = {
        "pipelineTasks": [
            {
                "taskType": "translation",
                "config": {
                    "language": {
                        "sourceLanguage": LANG_CODES.get(src_lang, "en"),
                        "targetLanguage": LANG_CODES.get(tgt_lang, "hi")
                    }
                }
            }
        ],
        "pipelineRequestConfig": {
            "pipelineId": PIPELINE_ID
        }
    }

    headers = {
        "userID":     BHASHINI_USER_ID,
        "ulcaApiKey": BHASHINI_API_KEY,
        "Content-Type": "application/json"
    }

    try:
        resp = requests.post(url, json=payload, headers=headers, timeout=10)
        if resp.status_code == 200:
            return resp.json()
        else:
            print(f"[Bhashini] Pipeline search failed: HTTP {resp.status_code}")
            return None
    except Exception as ex:
        print(f"[Bhashini] Pipeline search exception: {ex}")
        return None


# ──────────────────────────────────────────────────────────────
#  STEP 2 of Bhashini two-step API: actually translate
# ──────────────────────────────────────────────────────────────
def translate_text(text: str, src_lang: str = "english", tgt_lang: str = "hindi") -> str:
    """
    Translate text using Bhashini IndicTrans2.
    Falls back to the original text on any failure so the chatbot
    keeps working even when Bhashini is unreachable.
    """
    if src_lang == tgt_lang or not text.strip():
        return text

    # No API keys configured → skip API call
    if not BHASHINI_USER_ID or not BHASHINI_API_KEY:
        print("[Bhashini] No API keys set — skipping translation.")
        return text

    pipeline_data = _get_pipeline_config(src_lang, tgt_lang)
    if not pipeline_data:
        return text   # graceful fallback

    try:
        pipeline_responses = pipeline_data.get("pipelineResponseConfig", [])
        if not pipeline_responses:
            return text

        task_configs = pipeline_responses[0].get("config", [])
        if not task_configs:
            return text

        service_id   = task_configs[0].get("serviceId", "")
        endpoint     = pipeline_data.get("pipelineInferenceAPIEndPoint", {})
        callback_url = endpoint.get("callbackUrl", "")
        key_name     = endpoint.get("inferenceApiKey", {}).get("name", "Authorization")
        key_value    = endpoint.get("inferenceApiKey", {}).get("value", "")

        if not callback_url:
            return text

        trans_payload = {
            "pipelineTasks": [
                {
                    "taskType": "translation",
                    "config": {
                        "language": {
                            "sourceLanguage": LANG_CODES.get(src_lang, "en"),
                            "targetLanguage": LANG_CODES.get(tgt_lang, "hi")
                        },
                        "serviceId": service_id
                    }
                }
            ],
            "inputData": {
                "input": [{"source": text}]
            }
        }

        trans_headers = {
            key_name: key_value,
            "Content-Type": "application/json"
        }

        r = requests.post(callback_url, json=trans_payload,
                          headers=trans_headers, timeout=15)

        if r.status_code == 200:
            result    = r.json()
            translated = (result
                          .get("pipelineResponse", [{}])[0]
                          .get("output",           [{}])[0]
                          .get("target", text))
            return translated
        else:
            print(f"[Bhashini] Translation call failed: HTTP {r.status_code}")
            return text

    except Exception as ex:
        print(f"[Bhashini] Translation exception: {ex}")
        return text


# ──────────────────────────────────────────────────────────────
#  Language detection (Devanagari script check)
# ──────────────────────────────────────────────────────────────
def detect_language(text: str) -> str:
    """
    Returns 'hindi' if the message contains Devanagari characters,
    otherwise 'english'.
    Unicode block U+0900–U+097F = Devanagari.
    """
    hindi_char_count = sum(1 for ch in text if '\u0900' <= ch <= '\u097F')
    return "hindi" if hindi_char_count > 1 else "english"


# ──────────────────────────────────────────────────────────────
#  Hinglish / code-mixed text handler
#  Handles phrases like "mera aadhaar kho gaya"
# ──────────────────────────────────────────────────────────────
HINGLISH_MAP = {
    # common romanised Hindi words users type
    "kisan":    "किसान",
    "aadhaar":  "आधार",
    "adhar":    "आधार",
    "gaon":     "गांव",
    "ghar":     "घर",
    "paisa":    "पैसा",
    "paise":    "पैसे",
    "khet":     "खेत",
    "zameen":   "जमीन",
    "sarkar":   "सरकार",
    "yojana":   "योजना",
    "pension":  "पेंशन",
    "majdur":   "मजदूर",
    "naukar":   "नौकर",
    "kaam":     "काम",
    "gareeb":   "गरीब",
    "berojgar": "बेरोजगार",
    "beti":     "बेटी",
    "beta":     "बेटा",
    "baccha":   "बच्चा",
    "rasoi":    "रसोई",
    "gas":      "गैस",
    "makaan":   "मकान",
    "loan":     "लोन",
    "byaaj":    "ब्याज",
    "bank":     "बैंक",
    "account":  "खाता",
}


def handle_hinglish(text: str) -> str:
    """
    Lightly normalises code-mixed Hinglish text so the
    keyword detector in app.py works more reliably.
    Does NOT attempt full transliteration — only a lookup table.
    """
    words  = text.split()
    result = []
    for w in words:
        lower = w.lower().rstrip(".,!?")
        result.append(HINGLISH_MAP.get(lower, w))
    return " ".join(result)
