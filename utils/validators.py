import re
from urllib.parse import urlparse

# Basic domain regex (strict but practical)
DOMAIN_REGEX = re.compile(
    r"^(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}$"
)

DISALLOWED_HOSTS = {
    "localhost",
    "127.0.0.1",
    "0.0.0.0"
}

def normalize_target(target: str) -> str:
    """
    Normalize input to a clean domain name.
    Examples:
        https://example.com -> example.com
        http://www.example.com -> example.com
        example.com -> example.com
    """
    target = target.strip()

    if not target:
        raise ValueError("Empty target provided")

    if "://" not in target:
        target = "http://" + target

    parsed = urlparse(target)
    hostname = parsed.hostname

    if not hostname:
        raise ValueError("Invalid URL format")

    hostname = hostname.lower().lstrip("www.")

    return hostname


def is_valid_domain(domain: str) -> bool:
    """
    Validate domain against regex and block unsafe hosts.
    """
    if domain in DISALLOWED_HOSTS:
        return False

    return bool(DOMAIN_REGEX.match(domain))


def validate_target(target: str) -> str:
    """
    Full validation pipeline.
    Returns normalized domain if valid, else raises ValueError.
    """
    domain = normalize_target(target)

    if not is_valid_domain(domain):
        raise ValueError("Target is not a valid public domain")

    return domain
