from flask import Flask, render_template, request, jsonify
import mysql.connector
import pandas as pd
import os

app = Flask(__name__)
os.makedirs("uploads", exist_ok=True)

# ------------------ DATABASE CONNECTION ------------------
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Karthik@26",
    database="soil_db"
)
cursor = db.cursor(dictionary=True)

# ------------------ TRANSLATIONS ------------------
translations = {
    "acidic": {
        "en": "⚠️ Soil acidic → Apply lime before sowing.",
        "kn": "⚠️ ಮಣ್ಣು ಆಮ್ಲೀಯವಾಗಿದೆ → ಬೀಜ ಬಿತ್ತುವ ಮೊದಲು ಸುಣ್ಣ ಹಚ್ಚಿ.",
        "hi": "⚠️ मिट्टी अम्लीय है → बुवाई से पहले चुना डालें।",
        "te": "⚠️ నేల ఆమ్లత ఎక్కువగా ఉంది → విత్తనానికి ముందు చున్నం వేయండి.",
        "ta": "⚠️ மண் அமிலமாக உள்ளது → விதைக்கும் முன் சுண்ணாம்பு போடவும்.",
        "ml": "⚠️ മണ്ണ് അമ്ലീയം → വിതയ്ക്കുന്നതിന് മുമ്പ് ചുണ്ണാമ്പ് ചേർക്കുക."
    },
    "nitrogen": {
        "en": "⚠️ Nitrogen low → Apply Urea.",
        "kn": "⚠️ ನೈಟ್ರೋಜನ್ ಕಡಿಮೆ → ಯೂರಿಯಾ ಹಚ್ಚಿ.",
        "hi": "⚠️ नाइट्रोजन कम है → यूरिया डालें।",
        "te": "⚠️ నత్రజని తక్కువగా ఉంది → యూరియా వేయండి.",
        "ta": "⚠️ நைட்ரஜன் குறைவாக உள்ளது → யூரியா போடவும்.",
        "ml": "⚠️ നൈട്രജൻ കുറവ് → യൂരിയ ചേർക്കുക."
    },
    "phosphorus": {
        "en": "⚠️ Phosphorus low → Apply DAP.",
        "kn": "⚠️ ಫಾಸ್ಫರಸ್ ಕಡಿಮೆ → ಡಿಎಪಿ ಹಚ್ಚಿ.",
        "hi": "⚠️ फास्फोरस कम है → डीएपी डालें।",
        "te": "⚠️ ఫాస్ఫరస్ తక్కువగా ఉంది → డిఏపీ వేయండి.",
        "ta": "⚠️ பாஸ்பரஸ் குறைவாக உள்ளது → டிஏபி போடவும்.",
        "ml": "⚠️ ഫോസ്ഫറസ് കുറവ് → ഡി.എ.പി ചേർക്കുക."
    },
    "potassium": {
        "en": "⚠️ Potassium low → Apply MOP.",
        "kn": "⚠️ ಪೊಟಾಷಿಯಂ ಕಡಿಮೆ → ಎಮ್.ಓ.ಪಿ ಹಚ್ಚಿ.",
        "hi": "⚠️ पोटैशियम कम है → एमओपी डालें।",
        "te": "⚠️ పొటాషియం తక్కువగా ఉంది → ఎమ్‌ఓపీ వేయండి.",
        "ta": "⚠️ பொட்டாசியம் குறைவாக உள்ளது → எம்.ஓ.பி போடவும்.",
        "ml": "⚠️ പൊട്ടാസ്യം കുറവ് → എം.ഒ.പി ചേർക്കുക."
    },
    "healthy": {
        "en": "✅ Soil is healthy 👍",
        "kn": "✅ ಮಣ್ಣು ಆರೋಗ್ಯಕರವಾಗಿದೆ 👍",
        "hi": "✅ मिट्टी स्वस्थ है 👍",
        "te": "✅ నేల ఆరోగ్యంగా ఉంది 👍",
        "ta": "✅ மண் ஆரோக்கியமாக உள்ளது 👍",
        "ml": "✅ മണ്ണ് ആരോഗ്യകരമാണ് 👍"
    }
}

# ------------------ HELPER ------------------
def get_recommendations(data, lang="en"):
    advice = []
    if float(data.get("ph", 7)) < 5.5:
        advice.append(translations["acidic"][lang])
    if float(data.get("nitrogen", 0)) < 150:
        advice.append(translations["nitrogen"][lang])
    if float(data.get("phosphorus", 0)) < 12:
        advice.append(translations["phosphorus"][lang])
    if float(data.get("potassium", 0)) < 150:
        advice.append(translations["potassium"][lang])
    if not advice:
        advice.append(translations["healthy"][lang])
    return advice

# ------------------ ROUTES ------------------
@app.route("/")
def home():
    return render_template("form.html")

@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.json
    lang = data.get("lang", "en")  # default English

    # Save into MySQL
    sql = """INSERT INTO soil_samples
    (farmer_name, contact, field_id, location, ph, ec, moisture, organic_carbon, nitrogen, phosphorus, potassium)
    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
    cursor.execute(sql, (
        data.get("farmerName"), data.get("contact"), data.get("fieldId"),
        data.get("location"), data.get("ph"), data.get("ec"),
        data.get("moisture"), data.get("organic_carbon"), data.get("nitrogen"),
        data.get("phosphorus"), data.get("potassium")
    ))
    db.commit()

    # Multilingual recommendations
    advice = get_recommendations(data, lang)

    return jsonify({"recommendation": advice})

@app.route("/upload_csv", methods=["POST"])
def upload_csv():
    file = request.files["file"]
    lang = request.form.get("lang", "en")  # language from form
    filepath = os.path.join("uploads", file.filename)
    file.save(filepath)

    df = pd.read_csv(filepath)
    recommendations = []

    for _, row in df.iterrows():
        sql = """INSERT INTO soil_samples
        (farmer_name, contact, field_id, location, ph, ec, moisture, organic_carbon, nitrogen, phosphorus, potassium)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
        cursor.execute(sql, tuple(row))

        advice = get_recommendations(row, lang)
        recommendations.append({
            "farmer": row["farmer_name"],
            "field": row["field_id"],
            "recommendation": advice
        })

    db.commit()
    return jsonify({
        "message": translations["healthy"][lang],  # confirmation in local language
        "results": recommendations
    })

if __name__ == "__main__":
    app.run(debug=True)
