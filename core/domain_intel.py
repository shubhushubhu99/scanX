import socket
import ssl
import datetime
import requests


DEFAULT_TIMEOUT = 5


def check_https(domain: str) -> bool:
    """
    Check if HTTPS is available for the domain.
    """
    try:
        response = requests.get(
            f"https://{domain}",
            timeout=DEFAULT_TIMEOUT,
            verify=True
        )
        return response.status_code < 500
    except requests.exceptions.RequestException:
        return False


def get_ssl_info(domain: str) -> dict:
    """
    Fetch basic SSL certificate details.
    """
    result = {
        "present": False,
        "issuer": None,
        "valid_from": None,
        "valid_to": None,
        "expired": None
    }

    try:
        context = ssl.create_default_context()
        with socket.create_connection((domain, 443), timeout=DEFAULT_TIMEOUT) as sock:
            with context.wrap_socket(sock, server_hostname=domain) as ssock:
                cert = ssock.getpeercert()

        result["present"] = True
        result["issuer"] = dict(x[0] for x in cert.get("issuer", []))
        result["valid_from"] = cert.get("notBefore")
        result["valid_to"] = cert.get("notAfter")

        expiry = datetime.datetime.strptime(
            result["valid_to"], "%b %d %H:%M:%S %Y %Z"
        )
        result["expired"] = expiry < datetime.datetime.utcnow()

    except Exception:
        pass

    return result


def domain_intelligence(domain: str) -> dict:
    """
    Main domain intelligence collector.
    """
    intel = {
        "domain": domain,
        "https": False,
        "ssl": {},
        "reachable": False
    }

    try:
        requests.get(
            f"http://{domain}",
            timeout=DEFAULT_TIMEOUT
        )
        intel["reachable"] = True
    except requests.exceptions.RequestException:
        intel["reachable"] = False

    intel["https"] = check_https(domain)

    if intel["https"]:
        intel["ssl"] = get_ssl_info(domain)
    else:
        intel["ssl"] = {"present": False}

    return intel
