from flask import Flask, send_from_directory
import mysql.connector
from reportlab.pdfgen import canvas

app = Flask(__name__)

# --- DB Connection ---
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Karthik@26",
    database="soil_db"
)
cursor = db.cursor(dictionary=True)

# --- Report Generation Route ---
@app.route("/download_report/<int:id>")
def download_report(id):
    cursor.execute("SELECT * FROM soil_samples WHERE id=%s", (id,))
    row = cursor.fetchone()

    filename = f"uploads/report_{id}.pdf"
    c = canvas.Canvas(filename)
    c.drawString(100, 750, "Soil Analysis Report")
    c.drawString(100, 730, f"Farmer: {row['farmer_name']}")
    c.drawString(100, 710, f"pH: {row['ph']}, Nitrogen: {row['nitrogen']}")
    c.drawString(100, 690, "Recommendation: Apply Urea + DAP")
    c.save()

    return send_from_directory("uploads", f"report_{id}.pdf")
