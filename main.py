from flask import Flask, request, render_template, jsonify
import re
import dns.resolver  # pip install dnspython

app = Flask(__name__)

EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")

def has_mx_record(domain: str) -> bool:
    try:
        answers = dns.resolver.resolve(domain, "MX")
        return len(answers) > 0
    except Exception:
        return False

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/validate", methods=["POST"])
def validate_email():
    data = request.get_json()
    email = data.get("email", "")
    
    if not EMAIL_REGEX.match(email):
        return jsonify({"message": "❌ Invalid Email Address Format"})
    
    # Extract domain from email
    domain = email.split("@")[-1]
    
    # Check MX
