from flask import Flask, render_template, jsonify, request, send_from_directory
import pandas as pd
import os
from reportlab.pdfgen import canvas

# Import your DB connection and cursor from models.py
from backend.models import db, cursor

# Import bot-related functions
from backend.bot import translate_text, predict_temperature, predict_rainfall, recommend_crop

app = Flask(__name__)
os.makedirs("uploads", exist_ok=True)


# ------------------ TRANSLATIONS for soil analysis ------------------
translations = {
    "acidic": {
        "en": "⚠️ Soil acidic → Apply lime before sowing.",
        "kn": "⚠️ ಮಣ್ಣು ಆಮ್ಲೀಯವಾಗಿದೆ → ಬೀಜ ಬಿತ್ತುವ ಮೊದಲು ಸುಣ್ಣ ಹಚ್ಚಿ.",
        "hi": "⚠️ मिट्टी अम्लीय है → बुवाई से पहले चुना डालें।",
        "te": "⚠️ నేల ఆమ్లత ఎక్కువగా ఉంది → విత్తనానికి ముందు చున్నం వేయండి.",
        "ta": "⚠️ மண் அமிலமாக உள்ளது → விதைக்கும் முன் சுண்ணாம்பு போடவும்.",
        "ml": "⚠️ മണ്ണ് അമ്ലീയം → വിതയ്ക്കുന്നതിനുമുമ്പ് ചുണ്ണാമ്പ് ചേർക്കുക."
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
        "te": "⚠️ పొటాషియం తక్కువగా ఉంది → ఎమ్‌ఓపీ వేశండి.",
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


# ------------------ UI texts ------------------
ui_texts = {
    "English": {"heading": "Farmers Learning Hub", "search": "Search for crops...", "button": "Search", "not_found": "Not found"},
    "Telugu": {"heading": "రైతుల అభ్యాస కేంద్రం", "search": "పంటలను వెతకండి...", "button": "వెతకండి", "not_found": "కనబడ లేదు"},
    "Kannada": {"heading": "ರೈತుల ಅಧ್ಯಯನ ಕೇಂದ್ರ", "search": "ಬೆಳೆಗಳನ್ನು ಹುಡುಕಿ...", "button": "ಹುಡುಕು", "not_found": "ಸಿಕ್ಕಲಿಲ್ಲ"},
    "Tamil": {"heading": "விவசாயிகள் கற்றல் மையம்", "search": "பயிர்களைத் தேடுங்கள்...", "button": "தேடு", "not_found": "கிடைக்கவில்லை"},
    "Malayalam": {"heading": "കർഷകരുടെ പഠന കേന്ദ്രം", "search": "വിളകൾ തിരയുക...", "button": "തിരയുക", "not_found": "കണ്ടുപിടിക്കുന്നില്ല"}
}


# ------------------ Crops ------------------
crops = {
    "wheat": {
        "English": {"name": "Wheat", "description": "Wheat is a rabi cereal crop grown in cool climates. Needs moderate irrigation and well-drained soil.", "video": "https://www.youtube.com/embed/SJv8bHTq4mU"},
        "Telugu": {"name": "గోధుమ", "description": "గోధుమ రబీ ధాన్యం, చల్లని వాతావరణంలో పెరుగుతుంది. మితమైన నీటి అవసరం మరియు బాగా డ్రెయిన్ అయ్యే నేల కావాలి.", "video": "https://www.youtube.com/embed/SJv8bHTq4mU"},
        "Kannada": {"name": "ಗೋಧಿ", "description": "ಗೋಧಿ ರಬಿ ಧಾನ್ಯವಾಗಿದ್ದು ತಂಪು ಹವಾಮಾನದಲ್ಲೇ ಬೆಳೆಯುತ್ತದೆ. ಮಿತವಾದ ನೀರಾವರಿ ಮತ್ತು ಉತ್ತಮ ನೀರು ಹರಿದುಹೋಗುವ ಮಣ್ಣು ಬೇಕು.", "video": "https://www.youtube.com/embed/SJv8bHTq4mU"},
        "Tamil": {"name": "கோதுமை", "description": "கோதுமை ரபி பயிர்; குளிர்ந்த காலநிலைகளில் வளரும். மிதமான பாசனம் மற்றும் நன்கு வடிகட்டும் மண் தேவை.", "video": "https://www.youtube.com/embed/SJv8bHTq4mU"},
        "Malayalam": {"name": "ഗോതമ്പ്", "description": "ഗോതമ്പ് റബ്ബി ധാന്യം ആണ്, തണുത്ത കാലാവസ്ഥയില് വളരുന്നു. മිතമായ ജലസേചനവും നല്ല ഡ്രെയിനും ആവശ്യമാണ്.", "video": "https://www.youtube.com/embed/SJv8bHTq4mU"}
    },
    "rice": {
        "English": {"name": "Rice", "description": "Rice is a staple crop often grown in flooded fields; prefers warm temperatures and abundant water.", "video": "https://www.youtube.com/embed/FW_bw9jdrlQ"},
        "Telugu": {"name": "బియ్యం", "description": "బియ్యం నీటితో నింపిన పొలాల్లో పెరుగుతుంది; వేడి వాతావరణం మరియు ఎక్కువ నీరు అవసరం.", "video": "https://www.youtube.com/embed/FW_bw9jdrlQ"},
        "Kannada": {"name": "ಅನ್ನ", "description": "ಅನ್ನ ನೀರಿನಿಂದ ತುಂಬಿದ ತೋಟಗಳಲ್ಲಿ ಬೆಳೆಯುತ್ತದೆ; ಬಿಸಿ ಹವಾಮಾನ ಮತ್ತು ಹೆಚ್ಚು ಜಲಾವಶ್ಯಕತೆ.", "video": "https://www.youtube.com/embed/FW_bw9jdrlQ"},
        "Tamil": {"name": "அரிசி", "description": "அரிசி வெவ்வேறு நீர்த்தே needா வயல்கள்; வெப்பமான இடம் மற்றும் அதிக நீர் தேவை.", "video": "https://www.youtube.com/embed/FW_bw9jdrlQ"},
        "Malayalam": {"name": "അരി", "description": "അരി വെള്ളമുള്ള വയലുകളിൽ വളരുന്നു; ചൂട് കാലാവസ്ഥയും അധിക ജലവും ആവശ്യം.", "video": "https://www.youtube.com/embed/FW_bw9jdrlQ"}
    },
    "maize": {
        "English": {"name": "Maize", "description": "Maize is a kharif cereal crop requiring warm weather and moderate rainfall.", "video": "https://www.youtube.com/embed/yXuYFhQOqGQ"},
        "Telugu": {"name": "మొక్కజొన్న", "description": "మొక్కజొన్న ఖరీఫ్ ధాన్యం, వేడి వాతావరణం మరియు మితమైన వర్షపాతం అవసరం.", "video": "https://www.youtube.com/embed/yXuYFhQOqGQ"},
        "Kannada": {"name": "ಸೊಪ್ಪು ಜೋಳ", "description": "ಸೊಪ್ಪು ಜೋಳ ಖರಿಫ್ ಧಾನ್ಯ, ಬಿಸಿಲು ಹವಾಮಾನ ಮತ್ತು ಮಧ್ಯಮ ಮಳೆಯ ಅಗತ್ಯ.", "video": "https://www.youtube.com/embed/yXuYFhQOqGQ"},
        "Tamil": {"name": "சோளம்", "description": "சோளம் ஒரு க்ராஃப் பயிர்; வெப்பமான இடம் மற்றும் மிதமான மழை தேவை.", "video": "https://www.youtube.com/embed/yXuYFhQOqGQ"},
        "Malayalam": {"name": "മക്കാ", "description": "മക്ക ഒരു ഖരിഫ് ധാന്യം; ചൂട് കാലാവസ്ഥയും മിതമായ മഴയും ആവശ്യം.", "video": "https://www.youtube.com/embed/yXuYFhQOqGQ"}
    },
    "tomato": {
        "English": {"name": "Tomato", "description": "Tomato is a Kharif vegetable crop; requires well-drained soil and warm weather.", "video": "https://www.youtube.com/embed/F7lIP9lmLlo"},
        "Telugu": {"name": "టమోటా", "description": "టమోటా ఖరీఫ్ కూరగాయ, బాగా డ్రెయిన్ అయ్యే నేల మరియు వేడి వాతావరణం కావాలి.", "video": "https://www.youtube.com/embed/F7lIP9lmLlo"},
        "Kannada": {"name": "ಟೊಮ್ಯಾಟೊ", "description": "ಟೊಮ್ಯಾಟೊ ಖರಿಫ್ ತರಕಾರಿಯಾಗಿದೆ; ಉತ್ತಮ ಡ್ರೆನ್ ಇರುವ ಮಣ್ಣು ಮತ್ತು ಬಿಸಿಯ ಹವಾಮಾನ ಅಗತ್ಯ.", "video": "https://www.youtube.com/embed/F7lIP9lmLlo"},
        "Tamil": {"name": "தக்காளி", "description": "தக்காளி ஒரு க்ராஃப் காய்கறி; நன்கு வடிகட்டும் மண் மற்றும் வெப்பமான இடம் தேவை.", "video": "https://www.youtube.com/embed/F7lIP9lmLlo"},
        "Malayalam": {"name": "തക്കാളി", "description": "തക്കാളി ഖരിഫ് പച്ചക്കറി; നല്ല ഡ്രെയിൻ ഉള്ള മണ്ണും ചൂട് കാലാവസ്ഥയും ആവശ്യം.", "video": "https://www.youtube.com/embed/F7lIP9lmLlo"}
    },
    "potato": {
        "English": {"name": "Potato", "description": "Potato is a rabi tuber crop; prefers well-drained loamy soil and cool climate.", "video": "https://www.youtube.com/embed/l0M_Ek-0a7k"},
        "Telugu": {"name": "ఆలుగడ్డ", "description": "ఆలుగడ్డ రబీ కందం పంట, బాగా డ్రెయిన్ అయ్యే మట్టిని మరియు చల్లని వాతావరణం ఇష్టం.", "video": "https://www.youtube.com/embed/l0M_Ek-0a7k"},
        "Kannada": {"name": "ಅಲೂಗಡ್ಡೆ", "description": "ಅಲೂಗಡ್ಡೆ ರಬಿ ಟ್ಯೂಬರ್ ಪೈರಿಸ್; ಉತ್ತಮ ಡ್ರೆನ್ ಇರುವ ಮಣ್ಣು ಮತ್ತು ತಂಪು ಹವಾಮಾನ ಬೇಕು.", "video": "https://www.youtube.com/embed/l0M_Ek-0a7k"},
        "Tamil": {"name": "உருளைக்கிழங்கு", "description": "உருளைக்கிழங்கு ரபி கிழங்கு பயிர்; நன்கு வடிகட்டும் மண் மற்றும் குளிர்ந்த காலநிலை விரும்பும்.", "video": "https://www.youtube.com/embed/l0M_Ek-0a7k"},
        "Malayalam": {"name": "ഉരുളക്കിഴങ്ങ്", "description": "ഉരുളക്കിഴങ്ങ് റബ്ബി ട്യൂബർ; നല്ല ഡ്രെയിൻ ഉള്ള മണ്ണും തണുത്ത കാലാവസ്ഥയും ആവശ്യം.", "video": "https://www.youtube.com/embed/l0M_Ek-0a7k"}
    },
    "onion": {
        "English": {"name": "Onion", "description": "Onion is a rabi bulb crop; requires fertile, well-drained soil and moderate irrigation.", "video": "https://www.youtube.com/embed/nxRQp4BJ0U0"},
        "Telugu": {"name": "ఉల్లిపాయ", "description": "ఉల్లిపాయ రబీ బల్బ్ పంట; సమృద్ధి, బాగా డ్రెయిన్ అయ్యే నేల మరియు మితమైన నీటి అవసరం.", "video": "https://www.youtube.com/embed/nxRQp4BJ0U0"},
        "Kannada": {"name": "ಈರುಳ್ಳಿ", "description": "ಈರುಳ್ಳಿ ರಬಿ ಬಲ್ಬ್ ಪೈರಿಸ್; ಫಲವತ್ತಾದ, ಉತ್ತಮ ಡ್ರೆನ್ ಇರುವ ಮಣ್ಣು ಮತ್ತು ಮಧ್ಯಮ ನೀರಾವರಿ ಬೇಕು.", "video": "https://www.youtube.com/embed/nxRQp4BJ0U0"},
        "Tamil": {"name": "வெங்காயம்", "description": "வெங்காயம் ரபி பூண்டு பயிர்; வளமான, நன்கு வடிகட்டும் மண் மற்றும் மிதமான பாசனம் தேவை.", "video": "https://www.youtube.com/embed/nxRQp4BJ0U0"},
        "Malayalam": {"name": "സവാള", "description": "സവാള റബ്ബി ബൾബ്; ഉത്തമം, നല്ല ഡ്രെയിൻ ഉള്ള മണ്ണും മിതമായ ജലസേചനവും ആവശ്യം.", "video": "https://www.youtube.com/embed/nxRQp4BJ0U0"}
    },
    "chilli": {
        "English": {"name": "Chilli", "description": "Chilli is a kharif spice crop; requires warm climate and well-drained soil.", "video": "https://www.youtube.com/embed/JXvL6ZTRzWk"},
        "Telugu": {"name": "మిర్చి", "description": "మిర్చి ఖరీఫ్ మసాలా పంట; వేడి వాతావరణం మరియు బాగా డ్రెయిన్ అయ్యే నేల కావాలి.", "video": "https://www.youtube.com/embed/JXvL6ZTRzWk"},
        "Kannada": {"name": "ಮೆಣಸು", "description": "ಮೆಣಸು ಖರಿಫ್ ಮಸಾಲೆ; ಬಿಸಿಲು ಹವಾಮಾನ ಮತ್ತು ಉತ್ತಮ ಡ್ರೆನ್ ಇರುವ ಮಣ್ಣು ಅಗತ್ಯ.", "video": "https://www.youtube.com/embed/JXvL6ZTRzWk"},
        "Tamil": {"name": "மிளகாய்", "description": "மிளகாய் க்ராஃப் மசாலா பயிர்; வெப்பமான இடம் மற்றும் நன்கு வடிகட்டும் மண் தேவை.", "video": "https://www.youtube.com/embed/JXvL6ZTRzWk"},
        "Malayalam": {"name": "മുളക്", "description": "മുളക് ഖരിഫ് മസാല; ചൂട് കാലാവസ്ഥയും നല്ല ഡ്രെയിൻ ഉള്ള മണ്ണും ആവശ്യം.", "video": "https://www.youtube.com/embed/JXvL6ZTRzWk"}
    },
    "cotton": {
        "English": {"name": "Cotton", "description": "Cotton is a kharif fiber crop; requires warm climate and moderate rainfall.", "video": "https://www.youtube.com/embed/2S1nKQ2IcoI"},
        "Telugu": {"name": "పత్తి", "description": "పత్తి ఖరీఫ్ తంతి పంట; వేడి వాతావరణం మరియు మితమైన వర్షపాతం అవసరం.", "video": "https://www.youtube.com/embed/2S1nKQ2IcoI"},
        "Kannada": {"name": "ಹತ್ತಿ", "description": "ಹತ್ತಿ ಖರಿಫ್ ಬಟ್ಟೆ; ಬಿಸಿಲು ಹವಾಮಾನ ಮತ್ತು ಮಧ್ಯಮ ಮಳೆಯ ಅಗತ್ಯ.", "video": "https://www.youtube.com/embed/2S1nKQ2IcoI"},
        "Tamil": {"name": "பருத்தி", "description": "பருத்தி க்ராஃப் நார் பயிர்; வெப்பமான இடம் மற்றும் மிதமான மழை தேவை.", "video": "https://www.youtube.com/embed/2S1nKQ2IcoI"},
        "Malayalam": {"name": "പറ്റി", "description": "പറ്റി ഖരിഫ് ഫൈബർ; ചൂട് കാലാവസ്ഥയും മിതമായ മഴയും ആവശ്യം.", "video": "https://www.youtube.com/embed/2S1nKQ2IcoI"}
    }
}


# ------------------ Schemes ------------------
schemes = {
    "Prime Minister Matsya Sampada Yojana": "https://pmmsy.dof.gov.in",
    "PM-KUSUM Scheme": "https://mnre.gov.in/solar/schemes/",
    "Sub-Mission on Agricultural Mechanization (SMAM)": "https://agrimachinery.nic.in",
    "National Agriculture Market Scheme (e-NAM)": "https://enam.gov.in",
    "Pradhan Mantri Kisan Samman Nidhi Yojana (PM-KISAN)": "https://pmkisan.gov.in",
    "Pradhan Mantri Fasal Bima Yojana (PMFBY)": "https://pmfby.gov.in",
    "Pradhan Mantri Krishi Sinchayee Yojana (PMKSY)": "https://pmksy.gov.in",
    "Pradhan Mantri Kisan Mandhan Scheme": "https://maandhan.in",
    "Kisan Credit Card (KCC) Scheme": "https://pmkisan.gov.in",
    "Soil Health Card Scheme": "https://soilhealth.dac.gov.in",
    "Agriculture Infrastructure Fund (AIF) Scheme": "https://agriinfra.dac.gov.in",
    "Krishi Udan Scheme": "https://www.civilaviation.gov.in/en/about-air-transport/krishi-udan",
    "Feed and Fodder Development Scheme": "https://dahd.nic.in",
    "Rashtriya Krishi Vikas Yojana (RKVY)": "https://rkvy.nic.in",
    "Paramparagat Krishi Vikas Yojana (PKVY)": "https://pgsindia-ncof.gov.in",
    "Farmer Development Certificate Scheme": "https://agricoop.nic.in",
    "Rashtriya Gokul Mission (RGM)": "https://dahd.nic.in/division/gokul-mission",
    "Dairy Entrepreneurship Development Scheme": "https://dahd.nic.in",
    "National Horticulture Mission": "https://nhb.gov.in",
    "National Mission for Sustainable Agriculture (NMSA)": "https://nmsa.dac.gov.in",
    "Seed Village Scheme": "https://seednet.gov.in",
    "Organic Farming Incentive Scheme": "https://pgsindia-ncof.gov.in",
    "Farmer Producer Organization (FPO)": "https://sfacindia.com",
    "Drones for Precision Farming": "https://agricoop.nic.in/en/drones",
    "National Beekeeping and Honey Mission Scheme": "https://nbb.gov.in"
}


# ------------------ Routes ------------------

@app.route('/')
def home():
    return render_template('home.html')


@app.route('/crop_recommend')
def crop_recommend():
    return render_template('bot.html')


@app.route('/farmhub')
def farmhub():
    languages = list(ui_texts.keys())
    return render_template('farmhub.html', languages=languages)


@app.route('/search')
def search():
    crop_q = request.args.get('crop', '').strip().lower()
    lang = request.args.get('lang', 'English')
    if lang not in ui_texts:
        lang = 'English'
    ui = ui_texts[lang]
    result = {"name": "", "description": "", "video": ""}
    if crop_q:
        for key, block in crops.items():
            if crop_q == key:
                result = block.get(lang, block.get('English', {}))
                break
            name_local = block.get(lang, {}).get('name', '').lower()
            name_en = block.get('English', {}).get('name', '').lower()
            if crop_q == name_local or crop_q == name_en:
                result = block.get(lang, block.get('English', {}))
                break
    if not result["name"]:
        result["name"] = ui.get("not_found", "Not found")
        result["description"] = ""
        result["video"] = ""
    return jsonify({"ui": ui, "crop": result})


@app.route('/schemes')
def schemes_page():
    return render_template('schemes.html', schemes=schemes)


@app.route('/get_link', methods=['POST'])
def get_link():
    scheme = request.form.get('scheme')
    link = schemes.get(scheme)
    if link:
        return jsonify({'url': link})
    else:
        return jsonify({'url': ''}), 404


@app.route('/women')
def women_page():
    return render_template('women.html')


@app.route('/weather')
def weather_page():
    return render_template('weather.html')


# ------------------ Soil Analysis ------------------
@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.json
    lang = data.get("lang", "en")
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
    advice = get_recommendations(data, lang)
    return jsonify({"recommendation": advice})
@app.route('/pest')
def pest():
    return render_template('pest.html')



@app.route("/upload_csv", methods=["POST"])
def upload_csv():
    file = request.files["file"]
    lang = request.form.get("lang", "en")
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
    return jsonify({"message": translations["healthy"][lang], "results": recommendations})


@app.route("/download_report/<int:id>")
def download_report(id):
    cursor.execute("SELECT * FROM soil_samples WHERE id=%s", (id,))
    row = cursor.fetchone()
    if not row:
        return "Report not found", 404
    filename = f"uploads/report_{id}.pdf"
    c = canvas.Canvas(filename)
    c.drawString(100, 750, "Soil Analysis Report")
    c.drawString(100, 730, f"Farmer: {row['farmer_name']}")
    c.drawString(100, 710, f"pH: {row['ph']}, Nitrogen: {row['nitrogen']}")
    recommendations = get_recommendations(row, "en")
    c.drawString(100, 690, "Recommendation: " + ", ".join([rec.replace("⚠️ ", "") for rec in recommendations]))
    c.save()
    return send_from_directory("uploads", f"report_{id}.pdf", as_attachment=True)


@app.route('/soil_analysis')
def soil_analysis_page():
    return render_template('soil.html')


if __name__ == '__main__':
    app.run(debug=True)
