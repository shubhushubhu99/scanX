import re
import requests
from bs4 import BeautifulSoup
from datetime import datetime


def fingerprint_content(domain: str) -> dict:
    result = {
        "title": None,
        "title_quality": "Unknown",
        "meta_description": None,
        "meta_quality": "Unknown",
        "language": "Unknown",
        "content_length": 0,
        "copyright_year": None,
        "contact_depth": "Unknown",
        "risk_signal": "Unknown"
    }

    url = f"https://{domain}"

    try:
        response = requests.get(
            url,
            timeout=10,
            allow_redirects=True,
            headers={"User-Agent": "Mozilla/5.0"}
        )
        html = response.text
        soup = BeautifulSoup(html, "html.parser")

        # 1️⃣ Title
        title = soup.title.string.strip() if soup.title and soup.title.string else ""
        result["title"] = title

        if len(title) < 10:
            result["title_quality"] = "Weak"
        elif len(title) < 30:
            result["title_quality"] = "Moderate"
        else:
            result["title_quality"] = "Strong"

        # 2️⃣ Meta description
        meta = soup.find("meta", attrs={"name": "description"})
        description = meta["content"].strip() if meta and meta.get("content") else ""
        result["meta_description"] = description

        if len(description) < 30:
            result["meta_quality"] = "Weak"
        elif len(description) < 80:
            result["meta_quality"] = "Moderate"
        else:
            result["meta_quality"] = "Strong"

        # 3️⃣ Language
        html_tag = soup.find("html")
        if html_tag and html_tag.get("lang"):
            result["language"] = html_tag["lang"]

        # 4️⃣ Content length
        text = soup.get_text(separator=" ", strip=True)
        result["content_length"] = len(text)

        # 5️⃣ Copyright year
        year_matches = re.findall(r"(19\d{2}|20\d{2})", text)
        if year_matches:
            years = sorted(set(int(y) for y in year_matches))
            result["copyright_year"] = years[-1]

        # 6️⃣ Contact depth (basic heuristic)
        if re.search(r"\b(phone|email|address)\b", text, re.I):
            result["contact_depth"] = "Rich"
        elif re.search(r"\b(contact us|support)\b", text, re.I):
            result["contact_depth"] = "Moderate"
        else:
            result["contact_depth"] = "Weak"

    except Exception:
        pass

    # 7️⃣ Risk inference
    weak_signals = 0

    if result["title_quality"] == "Weak":
        weak_signals += 1
    if result["meta_quality"] == "Weak":
        weak_signals += 1
    if result["content_length"] < 500:
        weak_signals += 1
    if result["contact_depth"] == "Weak":
        weak_signals += 1

    if weak_signals >= 3:
        result["risk_signal"] = "High"
    elif weak_signals == 2:
        result["risk_signal"] = "Moderate"
    else:
        result["risk_signal"] = "Low"

    return result
