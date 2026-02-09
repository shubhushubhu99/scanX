import ssl
import socket
import requests
from urllib.parse import urlparse


SECURITY_HEADERS = [
    "content-security-policy",
    "strict-transport-security",
    "x-frame-options",
    "x-content-type-options",
    "referrer-policy",
]


def analyze_security_posture(domain: str) -> dict:
    result = {
        "https_enabled": False,
        "tls_version": "Unknown",
        "security_headers": {},
        "missing_headers": [],
        "cookie_flags": {
            "secure": False,
            "httponly": False
        },
        "risk_signal": "Unknown"
    }

    url = f"https://{domain}"

    # 1️⃣ HTTPS + headers check
    try:
        response = requests.get(
            url,
            timeout=10,
            allow_redirects=True
        )

        result["https_enabled"] = response.url.startswith("https")

        headers = {
            k.lower(): v for k, v in response.headers.items()
        }

        for header in SECURITY_HEADERS:
            if header in headers:
                result["security_headers"][header] = headers[header]
            else:
                result["missing_headers"].append(header)

        # Cookie flags (best effort)
        cookies = response.headers.get("set-cookie", "")
        if "secure" in cookies.lower():
            result["cookie_flags"]["secure"] = True
        if "httponly" in cookies.lower():
            result["cookie_flags"]["httponly"] = True

    except Exception:
        pass

    # 2️⃣ TLS version check (best effort)
    try:
        context = ssl.create_default_context()
        with socket.create_connection((domain, 443), timeout=5) as sock:
            with context.wrap_socket(sock, server_hostname=domain) as ssock:
                result["tls_version"] = ssock.version()
    except Exception:
        pass

    # 3️⃣ Risk signal inference
    if not result["https_enabled"]:
        result["risk_signal"] = "High"
    elif len(result["missing_headers"]) >= 3:
        result["risk_signal"] = "Moderate"
    else:
        result["risk_signal"] = "Low"

    return result
