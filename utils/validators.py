# utils/validators.py

import ipaddress
import socket
from typing import Optional


def is_safe_host(domain: str) -> bool:
    """
    Resolve `domain` and verify that none of its IP addresses point to
    private, loopback, link-local, or otherwise reserved network ranges.

    scanX fetches user-supplied domains directly (live inspection, policy
    checks, security posture, content fingerprinting). Without this guard
    a caller could submit an internal hostname/IP (e.g. "127.0.0.1",
    "169.254.169.254" cloud metadata, or an RFC1918 address) and turn the
    scanner into an SSRF proxy against internal infrastructure.
    """
    try:
        addr_infos = socket.getaddrinfo(domain, None)
    except socket.gaierror:
        return False

    if not addr_infos:
        return False

    for info in addr_infos:
        ip_str = info[4][0]
        try:
            ip = ipaddress.ip_address(ip_str)
        except ValueError:
            return False

        if (
            ip.is_private
            or ip.is_loopback
            or ip.is_link_local
            or ip.is_reserved
            or ip.is_multicast
            or ip.is_unspecified
        ):
            return False

    return True


def validate_domain(raw_domain: str) -> Optional[str]:
    """
    Sanitize and SSRF-guard a user-supplied domain before it is used
    to make outbound requests.

    Returns the cleaned domain, or None if it should be rejected.
    """
    if not raw_domain:
        return None

    domain = raw_domain.strip().lower()

    # Drop any path/query the caller left attached (normalize_domain only
    # strips a scheme when the input starts with "http").
    domain = domain.split("/")[0].split("?")[0]

    if not domain or domain == "localhost":
        return None

    if not is_safe_host(domain):
        return None

    return domain
