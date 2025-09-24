from flask import Flask, render_template, jsonify, request

app = Flask(__name__)

# Serve Women front-end page
@app.route('/women')
def women_page():
    return render_template("women.html")

# Serve translation content API similar to FastAPI version
translations = {
    "en": {
        "community": "Join WhatsApp groups and Twitter community",
        "helpline": "National: 1800-123-456, State: 1800-987-654",
    },
    "hi": {
        "community": "WhatsApp समूह और Twitter समुदाय में शामिल हों",
        "helpline": "राष्ट्रीय: 1800-123-456, राज्य: 1800-987-654",
    },
    "kn": {
        "community": "WhatsApp ಗುಂಪುಗಳು ಮತ್ತು Twitter ಸಮುದಾಯದಲ್ಲಿ ಸೇರಿ",
        "helpline": "ರಾಷ್ಟ್ರೀಯ: 1800-123-456, ರಾಜ್ಯ: 1800-987-654",
    },
    "ta": {
        "community": "WhatsApp குழுக்களிலும் Twitter சமூகத்திலும் இணையுங்கள்",
        "helpline": "தேசியம்: 1800-123-456, மாநிலம்: 1800-987-654",
    }
}

@app.route('/api/content/<lang>/<section>')
def get_content(lang, section):
    lang_data = translations.get(lang, translations["en"])
    content = lang_data.get(section, "")
    return jsonify({"content": content})

if __name__ == "__main__":
    app.run(debug=True)
