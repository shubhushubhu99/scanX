# core/live_inspector.py

import requests
import socket
import re
from urllib.parse import urljoin

HEADERS = {
    "User-Agent": "scanX Trust Analyzer"
}

TIMEOUT = 10

COMMON_PATHS = {
    "contact_page": ["/contact", "/contact-us", "/support"],
    "help_center": ["/help", "/help-center", "/faq"],
    "refund_policy": ["/refund", "/refund-policy", "/returns"],
    "privacy_policy": ["/privacy", "/privacy-policy"],
    "terms": ["/terms", "/terms-of-service"]
}


def resolve_domain(domain: str) -> bool:
    try:
        socket.gethostbyname(domain)
        return True
    except socket.error:
        return False


def check_url(base_url: str, path: str) -> dict:
    url = urljoin(base_url, path)
    try:
        r = requests.get(url, headers=HEADERS, timeout=TIMEOUT, allow_redirects=True)
        return {
            "url": url,
            "status_code": r.status_code,
            "reachable": r.status_code < 500
        }
    except requests.RequestException:
        return {
            "url": url,
            "status_code": None,
            "reachable": False
        }


def extract_support_email(html: str) -> list:
    return list(set(re.findall(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", html)))


def inspect_site(domain: str) -> dict:
    base_url = f"https://{domain}"

    inspection = {
        "dns_resolves": resolve_domain(domain),
        "homepage": None,
        "pages": {},
        "support_emails": []
    }

    # Homepage check
    try:
        r = requests.get(base_url, headers=HEADERS, timeout=TIMEOUT)
        inspection["homepage"] = {
            "status_code": r.status_code,
            "reachable": r.status_code < 500
        }
        inspection["support_emails"] = extract_support_email(r.text)
        homepage_html = r.text
    except requests.RequestException:
        inspection["homepage"] = {
            "status_code": None,
            "reachable": False
        }
        homepage_html = ""

    # Check common transparency paths
    for category, paths in COMMON_PATHS.items():
        inspection["pages"][category] = []
        for path in paths:
            result = check_url(base_url, path)
            if result["reachable"]:
                inspection["pages"][category].append(result)

    # Deduce signals
    inspection["signals"] = {
        "has_support_page": bool(inspection["pages"]["contact_page"]),
        "has_help_center": bool(inspection["pages"]["help_center"]),
        "has_refund_policy": bool(inspection["pages"]["refund_policy"]),
        "has_privacy_policy": bool(inspection["pages"]["privacy_policy"]),
        "has_terms": bool(inspection["pages"]["terms"]),
        "support_email_found": bool(inspection["support_emails"])
    }

    return inspection
