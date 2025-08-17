from flask import Flask, request, render_template, jsonify
import re
import dns.resolver  # pip install dnspython
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")

def has_mx_record(domain: str) -> bool:
    try:
        answers = dns.resolver.resolve(domain, "MX")
        return len(answers) > 0
    except Exception as e:
        logger.error(f"MX lookup failed for domain {domain}: {e}")
        return False

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/validate", methods=["POST"])
def validate_email():
    try:
        data = request.get_json()
        email = data.get("email", "")

        if not EMAIL_REGEX.match(email):
            logger.info(f"Invalid format: {email}")
            return jsonify({"message": "❌ Invalid Email Address Format"})

        # Extract domain
        domain = email.split("@")[-1]
        logger.info(f"Checking MX records for domain: {domain}")

        if has_mx_record(domain):
            return jsonify({"message": "✅ Valid Email & MX record exists"})
        else:
            return jsonify({"message": "⚠️ Valid format but no MX record found"})

    except Exception as e:
        logger.exception(f"Unexpected error validating {email}: {e}")
        return jsonify({"message": f"❌ Error validating email: {str(e)}"}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
