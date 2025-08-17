from flask import Flask, request, render_template, jsonify
import re

app = Flask(__name__)

EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/validate", methods=["POST"])
def validate_email():
    data = request.get_json()
    email = data.get("email", "")
    if EMAIL_REGEX.match(email):
        return jsonify({"message": "✅ Valid Email Address"})
    else:
        return jsonify({"message": "❌ Invalid Email Address"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
