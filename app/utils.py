import requests
import pandas as pd
import plotly.express as px
import json
from datetime import datetime
import os

def check_breaches(email_or_username):
    url = f"https://leakcheck.io/api/public?check={email_or_username}"

    try:
        response = requests.get(url, timeout=10)

        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                return data
            else:
                return {"success": False, "error": "No data found"}
        else:
            return {"success": False, "error": f"Status {response.status_code}"}
    except requests.exceptions.RequestException as e:
        return {"success": False, "error": str(e)}

def generate_charts(breach_data):
    import pandas as pd
    import plotly.express as px

    timeline_fig = None

    if "sources" in breach_data:
        df = pd.DataFrame(breach_data["sources"])
        df = df[df["date"] != "Unknown"]  # filter out fake dates

        if not df.empty:
            df["date"] = pd.to_datetime(df["date"], format="%Y-%m", errors="coerce")
            df = df.dropna(subset=["date"])  # remove invalid rows
            df["year"] = df["date"].dt.year

            timeline_fig = px.histogram(df, x="year", nbins=len(df["year"].unique()),
                                        title="Combined Breaches by Year", labels={"year": "Year"})

    return {
        "timeline": timeline_fig.to_html(full_html=False) if timeline_fig else None
    }

def clean_sources_light(sources):
    """
    Light cleaning:
    - Only keep sources that have a valid 'name' and 'date'
    - Ignore garbage, keep small breaches to preserve enough data
    """
    cleaned = []

    for breach in sources:
        name = breach.get("name", "").strip()
        date = breach.get("date", "").strip()

        if name and date and len(date) >= 7:  # date should be at least "YYYY-MM"
            cleaned.append({
                "name": name,
                "date": date
            })

    return cleaned

def save_search(query, breach_data, history_file="data/search_history.json"):
    # Create a new search record
    search_record = {
        "query": query,
        "timestamp": datetime.now().isoformat(),
        "found": breach_data.get("found", 0),
        "sources": breach_data.get("sources", [])
    }

    # Load existing history (or start fresh)
    if os.path.exists(history_file):
        with open(history_file, "r") as f:
            try:
                history = json.load(f)
            except json.JSONDecodeError:
                history = []
    else:
        history = []

    # Append the new record
    history.append(search_record)

    # Save it back
    with open(history_file, "w") as f:
        json.dump(history, f, indent=4)

def save_query_log(query, found_count, log_file="data/query_log.json"):
    record = {
        "query": query,
        "timestamp": datetime.now().isoformat(),
        "found": found_count
    }

    # Load or create
    if os.path.exists(log_file):
        with open(log_file, "r") as f:
            try:
                log = json.load(f)
            except json.JSONDecodeError:
                log = []
    else:
        log = []

    log.append(record)

    with open(log_file, "w") as f:
        json.dump(log, f, indent=4)

def add_to_watchlist(query, watchlist_file="data/watchlist.json"):
    query = query.strip().lower()
    
    if os.path.exists(watchlist_file):
        with open(watchlist_file, "r") as f:
            try:
                watchlist = json.load(f)
            except json.JSONDecodeError:
                watchlist = []
    else:
        watchlist = []

    # Don't add duplicates
    if query not in watchlist:
        watchlist.append(query)

        with open(watchlist_file, "w") as f:
            json.dump(watchlist, f, indent=4)

        return True  # Added successfully
    return False  # Already existed

def merge_breach_sources(leakcheck_sources, intelx_results):
    """
    Combine and sort breach sources from LeakCheck and IntelX by date descending.
    """
    combined = []

    # Add LeakCheck sources (assumed already cleaned)
    for breach in leakcheck_sources:
        if breach.get("name") and breach.get("date"):
            combined.append({
                "name": breach["name"],
                "date": breach["date"]
            })

    # Add IntelX selectors (no date, but we add them)
    selectors = intelx_results.get("selectors", []) if intelx_results else []
    for selector in selectors:
        combined.append({
            "name": selector.get("selectorvalue", "Unknown"),
            "date": "Unknown"  # No dates from IntelX
        })

    # Deduplicate by name
    seen = set()
    deduped = []
    for item in combined:
        if item["name"] not in seen:
            deduped.append(item)
            seen.add(item["name"])

    # Sort by date descending (Unknown goes last)
    def sort_key(b):
        return b["date"] if b["date"] != "Unknown" else ""

    deduped.sort(key=sort_key, reverse=True)
    return deduped
