import requests
import pandas as pd
import plotly.express as px

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
    timeline_fig = None

    if "sources" in breach_data:
        df = pd.DataFrame(breach_data["sources"])
        if not df.empty:
            df['date'] = pd.to_datetime(df['date'], format="%Y-%m")
            df['year'] = df['date'].dt.year
            timeline_fig = px.histogram(df, x="year", nbins=len(df['year'].unique()),
                                        title="Breaches by Year", labels={"year": "Year"})

    return {
        "timeline": timeline_fig.to_html(full_html=False) if timeline_fig else None
    }
