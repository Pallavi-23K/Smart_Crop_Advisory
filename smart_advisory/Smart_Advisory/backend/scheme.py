from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# Government schemes dictionary
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

@app.route("/")
def home():
    # Your home page route if used here, or serve home page from another file
    return render_template("home.html")

@app.route("/schemes")
def schemes_page():
    return render_template("schemes.html", schemes=schemes)

@app.route("/get_link", methods=["POST"])
def get_link():
    scheme = request.form.get("scheme")
    link = schemes.get(scheme)
    return jsonify({"url": link})

if __name__ == "__main__":
    app.run(debug=True)
