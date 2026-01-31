import socket
import datetime

try:
    import whois
except ImportError:
    whois = None


def inspect_infrastructure(domain: str) -> dict:
    result = {
        "domain_age_days": None,
        "domain_age_readable": "Unknown",
        "registrar": "Unknown",
        "name_servers": [],
        "dns_resolves": False,
        "risk_signal": "Unknown"
    }

    # 1️⃣ DNS resolution check
    try:
        socket.gethostbyname(domain)
        result["dns_resolves"] = True
    except Exception:
        result["dns_resolves"] = False

    # 2️⃣ WHOIS lookup (best effort)
    if whois:
        try:
            w = whois.whois(domain)

            # Domain age
            creation_date = w.creation_date
            if isinstance(creation_date, list):
                creation_date = creation_date[0]

            if creation_date:
                age_days = (datetime.datetime.utcnow() - creation_date).days
                result["domain_age_days"] = age_days

                if age_days < 180:
                    result["domain_age_readable"] = "Very New"
                elif age_days < 365:
                    result["domain_age_readable"] = "New"
                elif age_days < 1095:
                    result["domain_age_readable"] = "Established"
                else:
                    result["domain_age_readable"] = "Well Established"

            # Registrar
            if w.registrar:
                result["registrar"] = str(w.registrar)

            # Name servers
            if w.name_servers:
                result["name_servers"] = [
                    ns.lower() for ns in w.name_servers
                ]

        except Exception:
            pass  # WHOIS often fails, and that's OK

    # 3️⃣ Risk signal inference (simple, explainable)
    if result["domain_age_days"] is not None:
        if result["domain_age_days"] < 180:
            result["risk_signal"] = "High"
        elif result["domain_age_days"] < 365:
            result["risk_signal"] = "Moderate"
        else:
            result["risk_signal"] = "Low"

    return result
