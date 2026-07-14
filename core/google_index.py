# core/google_index.py

import os
import requests
from dotenv import load_dotenv

load_dotenv()

SERPAPI_KEY = os.getenv("SERPAPI_KEY")
BASE_URL = "https://serpapi.com/search.json"


def google_search(query: str, num_results: int = 5) -> list:
    """
    Perform a Google search using SerpAPI and return
    a list of evidence items (title, snippet, link).
    """
    if not SERPAPI_KEY:
        raise RuntimeError("SERPAPI_KEY not found in environment")

    params = {
        "engine": "google",
        "q": query,
        "api_key": SERPAPI_KEY,
        "num": num_results,
    }

    resp = requests.get(BASE_URL, params=params, timeout=30)
    resp.raise_for_status()
    data = resp.json()

    results = []
    for item in data.get("organic_results", []):
        results.append({
            "title": item.get("title", ""),
            "snippet": item.get("snippet", ""),
            "link": item.get("link", ""),
            "source": "google_index"
        })

    return results