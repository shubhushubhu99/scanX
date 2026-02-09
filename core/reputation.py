# core/reputation.py

from core.google_index import google_search


PLATFORM_QUERIES = {
    "Quora": 'site:quora.com "{domain}" legit',
    "Reddit": 'site:reddit.com "{domain}" review',
    "Trustpilot": 'site:trustpilot.com "{domain}"',
    "Forums": '"{domain}" user experience OR complaint',
    "Security": '"{domain}" data breach OR cyber attack'
}


def collect_public_signals(domain: str) -> dict:
    """
    Collect Google-indexed public evidence about a domain.
    Returns raw evidence + counts + strength.
    """
    evidence = {}
    total_mentions = 0

    for platform, template in PLATFORM_QUERIES.items():
        query = template.format(domain=domain)
        results = google_search(query, num_results=5)

        if results:
            evidence[platform] = results
            total_mentions += len(results)

    # Rule-based evidence strength (NO AI)
    if total_mentions >= 30:
        strength = "High"
    elif total_mentions >= 10:
        strength = "Medium"
    elif total_mentions > 0:
        strength = "Low"
    else:
        strength = "None"

    return {
        "domain": domain,
        "evidence": evidence,
        "total_mentions": total_mentions,
        "evidence_strength": strength,
        "platforms_checked": list(PLATFORM_QUERIES.keys()),
        "platforms_with_mentions": list(evidence.keys())
    }
