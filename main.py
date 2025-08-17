from flask import Flask, request, render_template, jsonify
import re
import dns.resolver  # pip install dnspython
import smtplib
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")


def has_mx_record(domain: str) -> str:
    """Check if MX record exists and return mail server"""
    try:
        answers = dns.resolver.resolve(domain, "MX")
        mx_record = str(answers[0].exchange).rstrip(".")
        return mx_record
    except Exception as e:
        logger.error(f"MX lookup failed for domain {domain}: {e}")
        return None


def smtp_check(email: str, mx_record: str) -> bool:
    """Try SMTP connection and RCPT TO check"""
    try:
        server = smtplib.SMTP(timeout=10)
        server.connect(mx_record)
        server.helo("example.com")  # pretend domain
        server.mail("test@example.com")  # fake sender
        code, message = server.rcpt(email)
        server.quit()
        logger.info(f"SMTP check for {email} -> {code} {message}")
        return code == 250
    except Exception as e:
        logger.error(f"SMTP validation failed for {email}: {e}")
        return False


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/validate", methods=["POST"])
def validate_email():
    results = {
        "format": "❌ Invalid format",
        "mx": "⏳ Skipped",
        "smtp": "⏳ Skipped"
    }

    try:
        data = request.get_json()
        email = data.get("email", "")

        # Step 1: Regex check
        if not EMAIL_REGEX.match(email):
            results["format"] = "❌ Invalid Email Address Format"
            return jsonify(results)

        results["format"] = "✅ Valid format"

        # Step 2: MX check
        domain = email.split("@")[-1]
        logger.info(f"Checking MX records for {domain}")
        mx_record = has_mx_record(domain)

        if not mx_record:
            results["mx"] = "❌ No MX record found"
            return jsonify(results)

        results["mx"] = f"✅ MX record found ({mx_record})"

        # Step 3: SMTP check
        if smtp_check(email, mx_record):
            results["smtp"] = "✅ Mailbox exists (SMTP confirmed)"
        else:
            results["smtp"] = "⚠️ MX found, but mailbox not confirmed"

        return jsonify(results)

    except Exception as e:
        logger.exception(f"Unexpected error validating {email}: {e}")
        results["smtp"] = f"❌ Error: {str(e)}"
        return jsonify(results), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
