import requests

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
