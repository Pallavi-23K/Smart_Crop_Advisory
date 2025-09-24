from flask import Flask, request, jsonify, render_template
from deep_translator import GoogleTranslator
from dateutil import parser
import math

app = Flask(__name__)

# --- Simple crop rules (expand as you like) ---
crop_rules = [
    {"soil": "clay",  "rainfall_min": 100, "rainfall_max": 300, "crop": "Paddy (Rice)"},
    {"soil": "clay",  "rainfall_min": 30,  "rainfall_max": 100, "crop": "Sugarcane"},
    {"soil": "loamy", "rainfall_min": 50,  "rainfall_max": 200, "crop": "Wheat"},
    {"soil": "loamy", "rainfall_min": 20,  "rainfall_max": 80,  "crop": "Maize"},
    {"soil": "sandy", "rainfall_min": 20,  "rainfall_max": 80,  "crop": "Millets"},
    {"soil": "sandy", "rainfall_min": 0,   "rainfall_max": 50,  "crop": "Groundnut"},
    # Add more rules as needed
]

SUPPORTED_LANGS = {
    "auto": "auto",
    "english": "en",
    "hindi": "hi",
    "kannada": "kn",
    "marathi": "mr",
    "telugu": "te",
    "tamil": "ta",
    "gujarati": "gu",
    "bengali": "bn",
    # add more language codes if desired
}


def translate_text(text, target_lang_code):
    """
    Use deep_translator.GoogleTranslator to translate text to target_lang_code.
    If target_lang_code is 'en' or translation fails, return original.
    """
    if not target_lang_code or target_lang_code == "en":
        return text
    try:
        return GoogleTranslator(source='auto', target=target_lang_code).translate(text)
    except Exception as e:
        # fallback to English if translation fails
        return text


def predict_temperature(latitude, month):
    """
    Simple, explainable heuristic temperature estimator:
    - Warmer near equator, colder near poles.
    - Small seasonal sine wave (northern hemisphere assumption by month).
    """
    lat = float(latitude)
    # base depends on latitude: 30°C at equator, decreases toward poles
    base = 30 - (abs(lat) / 90.0) * 25  # range roughly 5..30
    # seasonal component: month 1..12
    seasonal = 7 * math.cos((month - 1) / 12.0 * 2 * math.pi)  # +/-7°C seasonal
    temp = base + seasonal
    # clamp to reasonable range
    temp = max(-10, min(50, temp))
    return round(temp, 1)


def predict_rainfall(latitude, month):
    """
    Simple heuristic rainfall (mm/month):
    - Moderate base at mid-latitudes, less toward poles.
    - Seasonal effect (monsoon-like) modeled by sine wave.
    - This is a rough predictor for demo; replace with a real weather API or ML model for production.
    """
    lat = abs(float(latitude))
    # base rainfall decreases away from tropics mildly
    base = max(10, 200 - (lat / 90.0) * 160)  # ~40..200
    seasonal = 100 * (math.sin((month - 1) / 12.0 * 2 * math.pi) + 1) / 2  # 0..100
    rainfall = base + seasonal
    rainfall = max(0, rainfall)
    return int(round(rainfall))


def recommend_crop(soil, rainfall_mm):
    soil = soil.strip().lower()
    matches = []
    for rule in crop_rules:
        if rule["soil"].lower() == soil:
            if rule["rainfall_min"] <= rainfall_mm <= rule["rainfall_max"]:
                matches.append(rule["crop"])
    if matches:
        return matches
    # if no exact match, try broader suggestions based on soil only
    soil_suggestions = {
        "clay": ["Paddy (Rice)", "Sugarcane", "Banana"],
        "loamy": ["Wheat", "Maize", "Soybean"],
        "sandy": ["Millets", "Groundnut", "Cotton"]
    }
    return soil_suggestions.get(soil, ["Mixed vegetables", "Legumes"])


@app.route("/")
def index():
    return render_template("bot.html")


@app.route("/chat", methods=["POST"])
def chat():
    data = request.json or {}
    # Expected fields: language (name or code), soil, latitude, longitude, month (optional)
    lang = data.get("language", "english").lower()
    lang_code = SUPPORTED_LANGS.get(lang, lang if len(lang) <= 3 else "en")
    soil = data.get("soil", "").strip()
    lat = data.get("latitude", None)
    lon = data.get("longitude", None)
    month = data.get("month", None)

    # Validate
    if lat is None or lon is None or soil == "":
        bot_en = "Please provide soil type, latitude and longitude."
        bot = translate_text(bot_en, lang_code)
        return jsonify({"ok": False, "message": bot})

    try:
        lat = float(lat)
        lon = float(lon)
    except Exception:
        bot_en = "Latitude and longitude must be numeric."
        bot = translate_text(bot_en, lang_code)
        return jsonify({"ok": False, "message": bot})

    # month: if provided as date string, try parse; if numeric, use it
    try:
        if month:
            if isinstance(month, str):
                try:
                    parsed = parser.parse(month)
                    month_num = parsed.month
                except Exception:
                    month_num = int(month)
            else:
                month_num = int(month)
            if not (1 <= month_num <= 12):
                month_num = 1
        else:
            # default to current month (approx) — keep deterministic: use 1 (Jan) if not provided
            month_num = 1
    except Exception:
        month_num = 1

    # Predict temperature & rainfall
    temp_c = predict_temperature(lat, month_num)
    rainfall_mm = predict_rainfall(lat, month_num)

    # Recommend crops
    crops = recommend_crop(soil, rainfall_mm)

    # Build English message then translate
    bot_en = (
        f"Predicted temperature: {temp_c} °C.\n"
        f"Predicted monthly rainfall: {rainfall_mm} mm.\n"
        f"Recommended crop(s) for soil '{soil}': {', '.join(crops)}."
    )

    bot_translated = translate_text(bot_en, lang_code)

    # Return structured data too (numbers stay numbers)
    return jsonify({
        "ok": True,
        "language": lang,
        "language_code": lang_code,
        "message": bot_translated,
        "data": {
            "temperature_c": temp_c,
            "rainfall_mm": rainfall_mm,
            "recommended_crops": crops
        }
    })


if __name__ == "__main__":
    app.run(debug=True)
