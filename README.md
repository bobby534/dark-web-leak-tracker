# 🕵️‍♂️ Dark Web Leak Tracker

A Flask-based web application that checks if your email or username has appeared in data breaches using the **LeakCheck** and **IntelligenceX** APIs. The tool aggregates, deduplicates, and sorts breach data, providing users with a timeline graph and actionable features like watchlist tracking and CSV export.

---

## 🔍 Features

* ✅ Aggregate breach data from **LeakCheck** and **IntelX**
* 🧼 Deduplicate and sort breaches by date (descending)
* 📅 Visualize breaches over time using **Plotly**
* 📌 Persistent watchlist (with add/remove support)
* ⬇️ Export breach results to **CSV**
* ✉️ Auto-recheck script with **email alerts** via Gmail SMTP
* 💡 Flash messages for feedback (e.g., "Added to watchlist")
* ⚙️ Clean UI using **Bootstrap**

---

## 🛠️ Setup Instructions

```bash
# Clone the repo
git clone https://github.com/yourusername/dark-web-leak-tracker.git
cd dark-web-leak-tracker

# Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create your .env file for API keys and secrets
cp .env.example .env
# Then edit .env manually with your keys

# Run the app
python run.py
```

---

## 🔐 .env File Format

```env
INTELX_API_KEY=your_intelx_api_key_here
EMAIL_ADDRESS=your_gmail_address
EMAIL_PASSWORD=your_gmail_app_password
SECRET_KEY=your_flask_secret_key
```

Use a Gmail [app password](https://support.google.com/accounts/answer/185833) — not your actual email password.

---

## 🧾 File Structure

```
dark-web-leak-tracker/
├── app/
│   ├── __init__.py
│   ├── routes.py
│   ├── utils.py
│   ├── intelx_utils.py
│   └── templates/
│       └── index.html
├── data/
│   ├── search_history.json
│   ├── watchlist.json
│   ├── query_log.json
├── watchlist_checker.py
├── run.py
├── requirements.txt
├── .env
```

---

## 🧠 How It Works

* Submitting a query sends it to **LeakCheck** and **IntelX**
* Breach results are merged, deduplicated, and sorted by date
* A Plotly graph shows breach frequency by year
* You can save queries to a **watchlist** and get notified if new breaches appear
* A downloadable **CSV report** is generated for each search

---

## ✅ Final Notes

* Flash messages give real-time UI feedback for actions (add/remove)
* All breach info is local — no database setup required
* You can automate `watchlist_checker.py` with a cron job or task scheduler

---

### Made with Flask, APIs, Plotly, and a focus on usable threat intelligence.
