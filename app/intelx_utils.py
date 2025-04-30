import os
import requests
from dotenv import load_dotenv

load_dotenv()  # Load from .env

INTELX_API_KEY = os.getenv("INTELX_API_KEY")
BASE_URL = "https://2.intelx.io"

def search_intelx(query, max_results=5):
    headers = {
        "x-key": INTELX_API_KEY,
        "Content-Type": "application/json"
    }

    payload = {
        "term": query,
        "maxresults": max_results,
        "media": 0
    }

    try:
        response = requests.post(f"{BASE_URL}/intelligent/search", headers=headers, json=payload)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        return {"error": str(e)}
