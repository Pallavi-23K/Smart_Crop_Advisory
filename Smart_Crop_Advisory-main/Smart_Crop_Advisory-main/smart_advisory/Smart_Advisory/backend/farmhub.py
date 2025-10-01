from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# -------------------------------
# UI translations
# -------------------------------
ui_texts = {
    "English": {
        "heading": "Farmers Learning Hub",
        "search": "Search for crops...",
        "button": "Search",
        "not_found": "Not found"
    },
    "Telugu": {
        "heading": "రైతుల అభ్యాస కేంద్రం",
        "search": "పంటలను వెతకండి...",
        "button": "వెతకండి",
        "not_found": "కనబడలేదు"
    },
    "Kannada": {
        "heading": "ರೈತుల ಅಧ್ಯಯನ ಕೇಂದ್ರ",
        "search": "ಬೆಳೆಗಳನ್ನು ಹುಡುಕಿ...",
        "button": "ಹುಡುಕು",
        "not_found": "ಸಿಕ್ಕಲಿಲ್ಲ"
    },
    "Tamil": {
        "heading": "விவசாயிகள் கற்றல் மையம்",
        "search": "பயிர்களைத் தேடுங்கள்...",
        "button": "தேடு",
        "not_found": "கிடைக்கவில்லை"
    },
    "Malayalam": {
        "heading": "കർഷകരുടെ പഠന കേന്ദ്രം",
        "search": "വിളകൾ തിരയുക...",
        "button": "തിരയുക",
        "not_found": "കണ്ടുപിടിക്കുന്നില്ല"
    }
}

# -------------------------------
# Crops (14) with multilingual name, description and embedded video
# -------------------------------
crops = {
    "wheat": {
        "English": {
            "name": "Wheat",
            "description": "Wheat is a rabi cereal crop grown in cool climates. Needs moderate irrigation and well-drained soil.",
            "video": "https://www.youtube.com/embed/SJv8bHTq4mU"
        },
        "Telugu": {
            "name": "గోధుమ",
            "description": "గోధుమ రబీ ధాన్యం, చల్లని వాతావరణంలో పెరుగుతుంది. మితమైన నీటి అవసరం మరియు బాగా డ్రెయిన్ అయ్యే నేల కావాలి.",
            "video": "https://www.youtube.com/embed/SJv8bHTq4mU"
        },
        "Kannada": {
            "name": "ಗೋಧಿ",
            "description": "ಗೋಧಿ ರಬಿ ಧಾನ್ಯವಾಗಿದ್ದು ತಂಪು ಹವಾಮಾನದಲ್ಲೇ ಬೆಳೆಯುತ್ತದೆ. ಮಿತವಾದ ನೀರಾವರಿ ಮತ್ತು ಉತ್ತಮ ನೀರು ಹರಿದುಹೋಗುವ ಮಣ್ಣು ಬೇಕು.",
            "video": "https://www.youtube.com/embed/SJv8bHTq4mU"
        },
        "Tamil": {
            "name": "கோதுமை",
            "description": "கோதுமை ரபி பயிர்; குளிர்ந்த காலநிலைகளில் வளரும். மிதமான பாசனம் மற்றும் நன்கு வடிகட்டும் மண் தேவை.",
            "video": "https://www.youtube.com/embed/SJv8bHTq4mU"
        },
        "Malayalam": {
            "name": "ഗോതമ്പ്",
            "description": "ഗോതമ്പ് റബ്ബി ധാന്യം ആണ്, തണുത്ത കാലാവസ്ഥയില്‍ വളരുന്നു. മിതമായ ജലസേചനവും നല്ല ഡ്രെയിനും ആവശ്യമാണ്.",
            "video": "https://www.youtube.com/embed/SJv8bHTq4mU"
        }
    },
    "rice": {
        "English": {
            "name": "Rice",
            "description": "Rice is a staple crop often grown in flooded fields; prefers warm temperatures and abundant water.",
            "video": "https://www.youtube.com/embed/FW_bw9jdrlQ"
        },
        "Telugu": {
            "name": "బియ్యం",
            "description": "బియ్యం నీటితో నింపిన పొలాల్లో పెరుగుతుంది; వేడి వాతావరణం మరియు ఎక్కువ నీరు అవసరం.",
            "video": "https://www.youtube.com/embed/FW_bw9jdrlQ"
        },
        "Kannada": {
            "name": "ಅಕ್ಕಿ",
            "description": "ಅಕ್ಕಿ ಸಾಮಾನ್ಯವಾಗಿ ನೀರಿನಿಂದ ತುಂಬಿದ ಹೊಲಗಳಲ್ಲಿ ಬೆಳೆಯುತ್ತದೆ; ಬಿಸಿಲು ಮತ್ತು ಹೆಚ್ಚಿನ ನೀರು ಇಷ್ಟಪಡುತ್ತದೆ.",
            "video": "https://www.youtube.com/embed/FW_bw9jdrlQ"
        },
        "Tamil": {
            "name": "அரிசி",
            "description": "அரிசி தண்ணீரில் வளரக்கூடிய முக்கிய உண்ணுப் பயிர்; வெப்பத்தையும் நிறைந்த நீரையும் விரும்புகிறது.",
            "video": "https://www.youtube.com/embed/FW_bw9jdrlQ"
        },
        "Malayalam": {
            "name": "അരി",
            "description": "അരി വെള്ളം നിറച്ച നാടുകളിൽ വളരുന്നു; തണുത്ത് കുറവുള്ള വീതമുള്ള ചൂടും водой ആവശ്യമാണ്.",
            "video": "https://www.youtube.com/embed/FW_bw9jdrlQ"
        }
    },
    "maize": {
        "English": {
            "name": "Maize",
            "description": "Maize is a versatile kharif crop used for food and fodder; prefers warm weather and fertile soil.",
            "video": "https://www.youtube.com/embed/nfMLKP1nXK0"
        },
        "Telugu": {
            "name": "మొక్కజొన్న",
            "description": "మొక్కజొన్న ఆహారానికి, పశువులకు ఉపయోగపడుతుంది; వేడి వాతావరణం మరియు సారవంతమైన మట్టి ఇష్టపడుతుంది.",
            "video": "https://www.youtube.com/embed/nfMLKP1nXK0"
        },
        "Kannada": {
            "name": "ಜೋಳ",
            "description": "ಜೋಳ ಆಹಾರ ಮತ್ತು ಪಶುಮೇವುಗಳಿಗೆ ಉಪಯುಕ್ತ; ಬಿಸಿಯಾದ ಹವಾಮಾನ ಅಥವಾ ಫಲವತ್ತಾದ ಮಣ್ಣು ಬೇಕು.",
            "video": "https://www.youtube.com/embed/nfMLKP1nXK0"
        },
        "Tamil": {
            "name": "சோளம்",
            "description": "சோளம் பல பயன்களுக்கும் பயன்படும்; வெப்பமான காலநிலை மற்றும் வளமான மண் வேண்டும்.",
            "video": "https://www.youtube.com/embed/nfMLKP1nXK0"
        },
        "Malayalam": {
            "name": "ചോളം",
            "description": "ചോളം ഭക്ഷണത്തിനും മൃഗങ്ങളുടെ ചारा ആവശ്യത്തിനും ഉപയോഗിക്കുന്നു; ചൂട് കാലാവസ്ഥയും സാരമുള്ള മണ്ണും വേണം.",
            "video": "https://www.youtube.com/embed/nfMLKP1nXK0"
        }
    },
    "soyabean": {
        "English": {
            "name": "Soyabean",
            "description": "Soyabean is a protein-rich legume grown in warm seasons; used for oil, food and animal feed.",
            "video": "https://www.youtube.com/embed/BQ1jV_qEK_0"
        },
        "Telugu": {
            "name": "సోయాబీన్",
            "description": "సోయాబీన్ ప్రోటీన్ సమృద్ధిగా కలిగిన పంట; నూనె తయారీ, ఆహారం మరియు పశు ఆహారానికి ఉపయోగిస్తారు.",
            "video": "https://www.youtube.com/embed/BQ1jV_qEK_0"
        },
        "Kannada": {
            "name": "ಸೋಯಾಬೀನ್",
            "description": "ಸೋಯಾಬೀನ್ ಪ್ರೋಟೀನ್‌ರಿಂದ ತುಂಬಿದ ಪಲ್ಸು; ತೆಪ್ಪಾದ ಹವಾಮಾನದಲ್ಲೇ ಬೆಳೆಯುತ್ತದೆ ಮತ್ತು ನಿದೆಲೆಗೆ ಉಪಯೋಗಿ.",
            "video": "https://www.youtube.com/embed/BQ1jV_qEK_0"
        },
        "Tamil": {
            "name": "சோயாபீன்",
            "description": "சோயாபீன் புரதம் அதிகம் கொண்டது; எண்ணெய், உணவு மற்றும் மிருக உணவுக்கு பயன்படும்.",
            "video": "https://www.youtube.com/embed/BQ1jV_qEK_0"
        },
        "Malayalam": {
            "name": "സോയാബീൻ",
            "description": "സോയാബീൻ പ്രോട്ടീൻ സമ്പന്നമായതായുള്ള ലെഗ്യൂം; എണ്ണ, ആഹാരം, മൃഗാഹാരം എന്നിവയ്ക്ക് ഉപയോഗിക്കുന്നു.",
            "video": "https://www.youtube.com/embed/BQ1jV_qEK_0"
        }
    },
    "groundnut": {
        "English": {
            "name": "Groundnut (Peanut)",
            "description": "Groundnut is a legume grown in sandy soils; requires warm climate and proper drainage.",
            "video": "https://www.youtube.com/embed/0I7KR9Y8_4A"
        },
        "Telugu": {
            "name": "వేరుశెనగ",
            "description": "వేరుశెనగ ఇసుక మట్టిలో బాగా పెరుగుతుంది; వేడి వాతావరణం మరియు సరైన డ్రెయినేజ్ అవసరం.",
            "video": "https://www.youtube.com/embed/0I7KR9Y8_4A"
        },
        "Kannada": {
            "name": "ಕಡಲೆ",
            "description": "ಕಡಲೆ ಮರಳು ಮಣ್ಣಿನಲ್ಲಿ ಬೆಳೆದಾಗ ಉತ್ತಮ ಹುಳು ಹೊಡೆತ ಸಿಗುತ್ತದೆ; ಬಿಸಿಯ ಹವಾಮಾನ ಅಗತ್ಯ.",
            "video": "https://www.youtube.com/embed/0I7KR9Y8_4A"
        },
        "Tamil": {
            "name": "நிலக்கடலை",
            "description": "நிலக்கடலை மணலான மண்ணில் வளரும்; வெப்பமண்டலமும் நல்ல சொடுக்கம் தேவை.",
            "video": "https://www.youtube.com/embed/0I7KR9Y8_4A"
        },
        "Malayalam": {
            "name": "നെല്ലിക്കടല",
            "description": "നെല്ലിക്കടൽ മണലൽ മണ്ണിൽ വളരും; ചൂടും നന്നായ ഡ്രെയിനും ആവശ്യമാണ്.",
            "video": "https://www.youtube.com/embed/0I7KR9Y8_4A"
        }
    },
    "mustard": {
        "English": {
            "name": "Mustard",
            "description": "Mustard is an oilseed crop grown in winter; tolerates cool weather and needs fertile soil.",
            "video": "https://www.youtube.com/embed/UcmLV0b21Eg"
        },
        "Telugu": {
            "name": "ఆవాలు",
            "description": "ఆవాలు శిశిర కాలంలో పెరిగే నూనె పంట; చల్లని వాతావరణాన్ని సహించగలదు.",
            "video": "https://www.youtube.com/embed/UcmLV0b21Eg"
        },
        "Kannada": {
            "name": "ಸಾಸಿವೆ",
            "description": "ಸಾಸಿವೆ ಚಳಿಗಾಲದಲ್ಲಿ ಬೆಳೆದುವ ಎಣ್ಣೆ ಬೀಜ ಬೆಳೆ; ಫಲವತ್ತಾದ ಮಣ್ಣು ಅಗತ್ಯ.",
            "video": "https://www.youtube.com/embed/UcmLV0b21Eg"
        },
        "Tamil": {
            "name": "கடுகு",
            "description": "கடுகு குளிர்காலத்தில் வளரும் எண்ணெய் விதைப் பயிர்; வளமான மண் வேண்டும்.",
            "video": "https://www.youtube.com/embed/UcmLV0b21Eg"
        },
        "Malayalam": {
            "name": "കടുക്",
            "description": "കടുക് ശീതകാലതിൽ വളരുന്ന എണ്ണവിത്ത് വിളയാണ്; ഫ്ലാറ്റ് മണ്ണും ആവശ്യമാണ്.",
            "video": "https://www.youtube.com/embed/UcmLV0b21Eg"
        }
    },
    "cotton": {
        "English": {
            "name": "Cotton",
            "description": "Cotton is a fibre crop preferring black or loamy soils and warm climate; requires careful pest management.",
            "video": "https://www.youtube.com/embed/eN-TqqBQOAk"
        },
        "Telugu": {
            "name": "పత్తి",
            "description": "పత్తి నల్ల మట్టి లేదా లోమీ మట్టిని ఇష్టపడుతుంది, వేడి వాతావరణం అవసరం; పరాన్న ఆక్రమణలను నియంత్రించాలి.",
            "video": "https://www.youtube.com/embed/eN-TqqBQOAk"
        },
        "Kannada": {
            "name": "ಹತ್ತಿ",
            "description": "ಹತ್ತಿ ಕರಿ ಅಥವಾ ಲೊಮಿ ಮಣ್ಣನ್ನು ಇಷ್ಟಪಡುತ್ತದೆ ಮತ್ತು ಬಿಸಿಯಾದ ಹವಾಮಾನ ಅಗತ್ಯ; ಹೀಡು ಕೀಟ ನಿಯಂತ್ರಣ ಬಹುಮುಖ್ಯ.",
            "video": "https://www.youtube.com/embed/eN-TqqBQOAk"
        },
        "Tamil": {
            "name": "பருத்தி",
            "description": "பருத்தி கருப்பு அல்லது லோமி மண்ணையும் வெப்பநிலையையும் விரும்பும்; பூச்சி கட்டுப்பாடு அவசியம்.",
            "video": "https://www.youtube.com/embed/eN-TqqBQOAk"
        },
        "Malayalam": {
            "name": "പരുത്തി",
            "description": "പരുത്തി കരിഞ്ഞ്/ലോമി മണ്ണും ചൂടు കാലാവസ്ഥയും ഇഷ്ടപ്പെടും; കീട നിയന്ത്രണം പ്രധാനമാണ്.",
            "video": "https://www.youtube.com/embed/eN-TqqBQOAk"
        }
    },
    "tomato": {
        "English": {
            "name": "Tomato",
            "description": "Tomato is a warm-season vegetable; needs regular watering, staking and pest control for good yields.",
            "video": "https://www.youtube.com/embed/9seQurhbLPM"
        },
        "Telugu": {
            "name": "టమోటా",
            "description": "టమోటా మధ్యస్థ వాతావరణాన్ని ఇష్టపడుతుంది; నియమితులుగా నీరు, స్తేక్ మరియు పురుగు నియంత్రణ అవసరం.",
            "video": "https://www.youtube.com/embed/9seQurhbLPM"
        },
        "Kannada": {
            "name": "ಟೊಮ್ಯಾಟೊ",
            "description": "ಟೊಮ್ಯಾಟೊ ಮಧ್ಯಮ ತಾಪಮಾನದಲ್ಲಿ ಬೆಳೆಯುತ್ತದೆ; ನೀರು, ಬೆಂಬಲ ಮತ್ತು ಕೀಟ ನಿಯಂತ್ರಣ ಅಗತ್ಯ.",
            "video": "https://www.youtube.com/embed/9seQurhbLPM"
        },
        "Tamil": {
            "name": "தக்காளி",
            "description": "தக்காளி மிதமான வெப்பநிலையை விரும்பும்; அடிக்கடி நீர்ப்பாசனம், தண்டு ஆதரவு மற்றும் பூச்சி கட்டுப்பாடு தேவை.",
            "video": "https://www.youtube.com/embed/9seQurhbLPM"
        },
        "Malayalam": {
            "name": "തക്കാളി",
            "description": "തക്കാളി മിതമായ ചൂടില്‍ വളരുന്നു; പതിവായി ജലസേചനം, സ്തേക്ക്, കീട നിയന്ത്രണം ആവശ്യമാണ്.",
            "video": "https://www.youtube.com/embed/9seQurhbLPM"
        }
    },
    "potato": {
        "English": {
            "name": "Potato",
            "description": "Potato is a tuber crop grown in cool climates; needs loose, well-drained soil and hilling during growth.",
            "video": "https://www.youtube.com/embed/CEEiP-DfOfY"
        },
        "Telugu": {
            "name": "ఆలుగడ్డ",
            "description": "ఆలుగడ్డ చల్లని వాతావరణంలో పండే మూలిక పంట; సారసమైన, డ్రెయిన్ బాగా ఉన్న నేల మరియు హిల్లింగ్ అవసరం.",
            "video": "https://www.youtube.com/embed/CEEiP-DfOfY"
        },
        "Kannada": {
            "name": "ಆಲೂಗಡ್ಡೆ",
            "description": "ಆಲೂಗಡ್ಡೆ ತಂಪಾದ ಹವಾಮಾನದಲ್ಲಿ ಬೆಳೆಯುವ ಮೂಳೆಬೆಳೆ; ಸಡಿಲ ಮತ್ತು ಉತ್ತಮ ಡ್ರೇನ್ ಮಣ್ಣು ಹಾಗೂ ಹಿಲ್ಲಿಂಗ್ ಮುಖ್ಯ.",
            "video": "https://www.youtube.com/embed/CEEiP-DfOfY"
        },
        "Tamil": {
            "name": "உருளைக்கிழங்கு",
            "description": "உருளைக்கிழங்கு குளிரான நிலைகளில் வளரும்; சீரான, நன்கு வடிகட்டும் மண் மற்றும் மலைப்பணிகள் அவசியம்.",
            "video": "https://www.youtube.com/embed/CEEiP-DfOfY"
        },
        "Malayalam": {
            "name": "ഉരുളക്കിഴങ്ങ്",
            "description": "ഉരുളക്കിഴങ്ങ് തണുത്ത കാലാവസ്ഥയില്‍ പാടിടത്തില്‍ വളരുന്നു; കലസ്റ്റ് മണ്ണും ഹില്ലിങ്ങും ആവശ്യമാണ്.",
            "video": "https://www.youtube.com/embed/CEEiP-DfOfY"
        }
    },
    "onion": {
        "English": {
            "name": "Onion",
            "description": "Onion is a bulb crop grown in moderate climates; requires balanced fertilizer and adequate sunlight.",
            "video": "https://www.youtube.com/embed/ghm-LaOzeYg"
        },
        "Telugu": {
            "name": "ఉల్లిపాయ",
            "description": "ఉల్లిపాయ మితమైన వాతావరణంలో పెరుగుతుంది; సమతుల్య ఎరువులు మరియు సరిపడిన సూర్యకాంతి అవసరం.",
            "video": "https://www.youtube.com/embed/ghm-LaOzeYg"
        },
        "Kannada": {
            "name": "ಈರುಳ್ಳಿ",
            "description": "ಈರುಳ್ಳಿ ಮಧ್ಯಮ ಹವಾಮಾನದಲ್ಲಿ ಬೆಳೆಯುವ ಬಲ್ಬ್ ಬೆಳೆ; ಸಮತೋಲನವಾದ ಬೀಜು ಮತ್ತು ಸಾಕಷ್ಟು ಬೆಳಕು ಬೇಕು.",
            "video": "https://www.youtube.com/embed/ghm-LaOzeYg"
        },
        "Tamil": {
            "name": "வெங்காயம்",
            "description": "வெங்காயம் மிதமான காலநிலையில் வளர்கிறது; சரியான உரமும் கூடிய வெளிச்சமும் தேவை.",
            "video": "https://www.youtube.com/embed/ghm-LaOzeYg"
        },
        "Malayalam": {
            "name": "സവാള",
            "description": "സവാള മിതമായ കാലാവസ്ഥയില്‍ വളരുന്നു; ശരിയായ രാസംയും മതിയായ സൂര്യപ്രകാശവും ആവശ്യമാണ്.",
            "video": "https://www.youtube.com/embed/ghm-LaOzeYg"
        }
    },
    "chili": {
        "English": {
            "name": "Chili",
            "description": "Chili is a spice crop that thrives in warm and dry climates; needs fertile soil and pest care.",
            "video": "https://www.youtube.com/embed/pf07w8CNRJU"
        },
        "Telugu": {
            "name": "మిరపకాయ",
            "description": "మిరపకాయ వేడి, ఎక్కువగా ఎండ వాతావరణంలో పండుతుంది; సారవంతమైన నేల మరియు పురుగు నియంత్రణ అవసరం.",
            "video": "https://www.youtube.com/embed/pf07w8CNRJU"
        },
        "Kannada": {
            "name": "ಮೆಣಸು",
            "description": "ಮೆಣಸು ಬಿಸಿಲು ಮತ್ತು ಒಣ ಹವಾಮಾನವನ್ನು ಇಷ್ಟಪಡುತ್ತದೆ; ಫಲವತ್ತಾದ ಮಣ್ಣು ಮತ್ತು ಕೀಟ ನಿಯಂತ್ರಣ ಅಗತ್ಯ.",
            "video": "https://www.youtube.com/embed/pf07w8CNRJU"
        },
        "Tamil": {
            "name": "மிளகாய்",
            "description": "மிளகாய் வெப்பமான, வறண்ட காலநிலைகளில் சிறப்பாக வளரும்; நல்ல மண் மற்றும் பூச்சி கட்டுப்பாடு வேண்டும்.",
            "video": "https://www.youtube.com/embed/pf07w8CNRJU"
        },
        "Malayalam": {
            "name": "മുളക്",
            "description": "മുളക് ചൂടും വരണ്ട കാലാവസ്ഥയും ഇഷ്ടപ്പെടുന്നു; മികച്ച മണ്ണും കീടനിയന്ത്രണവും വേണം.",
            "video": "https://www.youtube.com/embed/pf07w8CNRJU"
        }
    },
    "banana": {
        "English": {
            "name": "Banana",
            "description": "Banana is a tropical perennial needing high rainfall or irrigation; requires rich soil and wind protection.",
            "video": "https://www.youtube.com/embed/h4N-QLhXjjY"
        },
        "Telugu": {
            "name": "అరటి",
            "description": "అరటి ఉష్ణమండల పంట; అధిక వర్షపాతం లేదా పంట నీరవిధానం అవసరం, సంపూర్ణ మట్టితో వృద్ధి.",
            "video": "https://www.youtube.com/embed/h4N-QLhXjjY"
        },
        "Kannada": {
            "name": "ಬಾಳೆಹಣ್ಣು",
            "description": "ಬಾಳೆಹಣ್ಣು ಉಷ್ಣಮಂಡಲದಲ್ಲേ ಬೆಳೆಯುತ್ತದೆ; ಹೆಚ್ಚಿನ ಮಳೆ ಅಥವಾ ನೀರಾವರಿ ಮತ್ತು ಬಲವಾದ ಮಣ್ಣು ಅಗತ್ಯ.",
            "video": "https://www.youtube.com/embed/h4N-QLhXjjY"
        },
        "Tamil": {
            "name": "வாழை",
            "description": "வாழை உஷ்ணமண்டலப் பயிர்; அதிக மழை அல்லது பாசனம், வளமான மண் மற்றும் காற்றிலிருந்து பாதுகாப்பு தேவை.",
            "video": "https://www.youtube.com/embed/h4N-QLhXjjY"
        },
        "Malayalam": {
            "name": "വാഴപ്പഴം",
            "description": "വാഴ ഉഷ്ണമേഖലയിലെ വളർച്ചക്കുള്ളതാണ്; മികവുറ്റ ബീജനം, കൂടുതല്‍ ജലസേചനം, കാറ്റില്‍നിന്ന് സംരക്ഷണം എന്നിവ ആവശ്യമാണ്.",
            "video": "https://www.youtube.com/embed/h4N-QLhXjjY"
        }
    },
    "mango": {
        "English": {
            "name": "Mango",
            "description": "Mango is a tropical fruit tree needing warm climate and well-drained soil; requires seasonal care for flowering and fruiting.",
            "video": "https://www.youtube.com/embed/0iAZa5bHQj0"
        },
        "Telugu": {
            "name": "మామిడి",
            "description": "మామిడి ఉష్ణమండలంలో పెరుగుతుంది; బాగా డ్రెయిన్ అయ్యే నేల మరియు పూవు/పండు సంరక్షణ అవసరం.",
            "video": "https://www.youtube.com/embed/0iAZa5bHQj0"
        },
        "Kannada": {
            "name": "ಮಾವು",
            "description": "ಮಾವು ಉಷ್ಣವಲಯದ ಹಣ್ಣು; ಚೆನ್ನಾಗಿ ಹರಿಯುವ ಮಣ್ಣು ಮತ್ತು ಹಂಗಾಮಿ ಆರೈಕೆ ಬೇಕು.",
            "video": "https://www.youtube.com/embed/0iAZa5bHQj0"
        },
        "Tamil": {
            "name": "மாம்பழம்",
            "description": "மாம்பழம் உஷ்ணமண்டலப் பழ மரம்; நன்கு வடிகட்டப்படும் மண் மற்றும் பருவப் பராமரிப்பு தேவை.",
            "video": "https://www.youtube.com/embed/0iAZa5bHQj0"
        },
        "Malayalam": {
            "name": "മാങ്ങ",
            "description": "മാങ്ങ ഒരു ഉഷ്ണമേഖലാ പഴവള്ളി; നല്ല ഡ്രെയ്ന്‍ മണ്ണും കാലിക പരിചരണവും ആവശ്യമാണ്.",
            "video": "https://www.youtube.com/embed/0iAZa5bHQj0"
        }
    },
    "apple": {
        "English": {
            "name": "Apple",
            "description": "Apple is a temperate fruit grown in cool, hilly regions; requires chill hours, well-drained soil and pruning.",
            "video": "https://www.youtube.com/embed/2zHe2mvdUU8"
        },
        "Telugu": {
            "name": "ఆపిల్",
            "description": "ఆపిల్ చల్లని పర్వత ప్రాంతాలలో పండుతుంది; చల్లిమొమదలు (chill hours), బాగా డ్రెయిన్ అయ్యే నేల మరియు ఖండితమైన నిపుణత అవసరం.",
            "video": "https://www.youtube.com/embed/2zHe2mvdUU8"
        },
        "Kannada": {
            "name": "ಸೇಬು",
            "description": "ಸೇಬು ತಂಪು ಪ್ರದೇಶಗಳಲ್ಲಿ ಬೆಳೆಯುವ ಹಣ್ಣು; ಚಿಲ್ ಅವರ್ಸ್, ಸರಿಯಾದ ಡ್ರೈನ್ ಮಣ್ಣು ಮತ್ತು ಕೈಗೊಳ್ಳುವಿಕೆ ಮುಖ್ಯ.",
            "video": "https://www.youtube.com/embed/2zHe2mvdUU8"
        },
        "Tamil": {
            "name": "ஆப்பிள்",
            "description": "ஆப்பிள் சளித்த மலைப்பகுதிகளிலும் வளருகிறது; 'சில்' நேரங்கள், நன்றாக வடிகட்டும் மண் மற்றும் கவனிப்பு தேவை.",
            "video": "https://www.youtube.com/embed/2zHe2mvdUU8"
        },
        "Malayalam": {
            "name": "ആപ്പിൾ",
            "description": "ആപ്പിൾ തണുത്ത, മലനിരപ്രദേശങ്ങളിൽ വളരുന്ന പഴം; ചിൽ മണിക്കൂറുകൾ, നല്ല ഡ്രെയിൻ, പ്രൂണിംഗ് എന്നിവ ആവശ്യമാണ്.",
            "video": "https://www.youtube.com/embed/2zHe2mvdUU8"
        }
    }
}

# -------------------------------
# Routes
# -------------------------------
@app.route("/")
def home():
    # Provide language options to template (keys from ui_texts)
    languages = list(ui_texts.keys())
    return render_template("farmhub.html", languages=languages)


@app.route("/search")
def search():
    """Return UI texts (for selected language) and matched crop (name, description, video)."""
    crop_q = request.args.get("crop", "").strip().lower()
    lang = request.args.get("lang", "English")
    if lang not in ui_texts:
        lang = "English"

    ui = ui_texts[lang]

    # default empty result
    result = {"name": "", "description": "", "video": ""}

    if crop_q:
        # try to match by key or by localized name or english name
        for key, block in crops.items():
            if crop_q == key:
                result = block.get(lang, block.get("English", {}))
                break
            # match by name in selected language or English
            name_local = block.get(lang, {}).get("name", "").lower()
            name_en = block.get("English", {}).get("name", "").lower()
            if crop_q == name_local or crop_q == name_en:
                result = block.get(lang, block.get("English", {}))
                break

    # if not found, set friendly not found name in selected language
    if not result["name"]:
        result["name"] = ui.get("not_found", "Not found")
        result["description"] = ""
        result["video"] = ""

    return jsonify({"ui": ui, "crop": result})


if __name__ == "__main__":
    app.run(debug=True)
