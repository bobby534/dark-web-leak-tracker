import json
import os
from datetime import datetime
from app.utils import check_breaches
from email.mime.text import MIMEText
import smtplib

WATCHLIST_FILE = "data/watchlist.json"
CHECK_HISTORY_FILE = "data/watchlist_checks.json"

EMAIL_ADDRESS = "kerry.lin3690@gmail.com"       # Your Gmail (or SMTP-enabled) address
EMAIL_PASSWORD = "lsvp omjn jlmf bkmx"    # App password (not your Gmail password!)
TO_EMAIL = "kerry.lin3690@gmail.com"

def load_watchlist():
    if os.path.exists(WATCHLIST_FILE):
        with open(WATCHLIST_FILE, "r") as f:
            return json.load(f)
    return []

def load_check_history():
    if os.path.exists(CHECK_HISTORY_FILE):
        with open(CHECK_HISTORY_FILE, "r") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return {}
    return {}

def save_check_history(history):
    with open(CHECK_HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=4)

def send_email_alert(query, new_sources):
    body = f"⚠️ New breach(es) detected for: {query}\n\n"
    for source in new_sources:
        body += f"- {source['name']} ({source['date']})\n"

    msg = MIMEText(body)
    msg["Subject"] = f"[Breach Alert] {query} - {len(new_sources)} new breaches"
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = TO_EMAIL

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        smtp.send_message(msg)

def check_watchlist():
    watchlist = load_watchlist()
    history = load_check_history()
    updated = False

    for query in watchlist:
        result = check_breaches(query)
        if result.get("success"):
            sources = result["sources"]
            cleaned = [s for s in sources if s.get("name") and s.get("date")]
            prev_sources = history.get(query, [])
            prev_names = {s["name"] for s in prev_sources}
            new_sources = [s for s in cleaned if s["name"] not in prev_names]

            if new_sources:
                send_email_alert(query, new_sources)
                history[query] = cleaned
                updated = True
        else:
            print(f"Error checking {query}: {result.get('error')}")

    if updated:
        save_check_history(history)

if __name__ == "__main__":
    print(f"🔄 Running watchlist check at {datetime.now().isoformat()}")
    check_watchlist()
