from flask import Flask, render_template, request

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def send_sms():
    result = None
    if request.method == "POST":
        phone = request.form.get("phone")
        message = request.form.get("message")
        if phone and message:
            result = f"Delivered to {phone}"
        else:
            result = " Please enter all details"
    return render_template("smss.html", result=result)

if __name__ == "__main__":
    app.run(debug=True)
