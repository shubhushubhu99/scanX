import requests

DEFAULT_TIMEOUT = 5

SECURITY_HEADERS = [
    "Content-Security-Policy",
    "Strict-Transport-Security",
    "X-Frame-Options",
    "X-Content-Type-Options",
    "Referrer-Policy",
    "Permissions-Policy"
]

EXPOSURE_HEADERS = [
    "Server",
    "X-Powered-By"
]


def fetch_headers(domain: str) -> dict:
    """
    Fetch HTTP headers from the target domain.
    """
    try:
        response = requests.get(
            f"http://{domain}",
            timeout=DEFAULT_TIMEOUT,
            allow_redirects=True
        )
        return response.headers
    except requests.exceptions.RequestException:
        return {}


def analyze_security_headers(headers: dict) -> dict:
    """
    Check presence of important security headers.
    """
    results = {}

    for header in SECURITY_HEADERS:
        results[header] = header in headers

    return results


def analyze_exposure(headers: dict) -> dict:
    """
    Detect technology exposure headers.
    """
    exposure = {}

    for header in EXPOSURE_HEADERS:
        exposure[header] = headers.get(header)

    return exposure


def check_robots(domain: str) -> bool:
    """
    Check if robots.txt is accessible.
    """
    try:
        response = requests.get(
            f"http://{domain}/robots.txt",
            timeout=DEFAULT_TIMEOUT
        )
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False


def content_scan(domain: str) -> dict:
    """
    Main content scanning function.
    """
    headers = fetch_headers(domain)

    return {
        "headers_found": bool(headers),
        "security_headers": analyze_security_headers(headers),
        "exposure": analyze_exposure(headers),
        "robots_txt": check_robots(domain)
    }
