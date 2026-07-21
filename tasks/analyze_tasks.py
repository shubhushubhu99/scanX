from celery_app import celery
from core.reputation import collect_public_signals
from core.live_inspector import inspect_site
from core.experience_miner import mine_experiences
from core.risk_engine import evaluate_risk
from core.policy_analyzer import analyze_policies
from core.policy_mismatch import detect_policy_mismatch
from core.trust_dimensions import evaluate_trust_dimensions
from agents.deep_explainer import explain_trust
from core.infra_intel import inspect_infrastructure
from core.security_posture import analyze_security_posture
from core.content_fingerprint import fingerprint_content

@celery.task(bind=True, name="analyze_domain_task")
def analyze_domain_task(self, domain, category):
    try:
        osint = collect_public_signals(domain)
        live = inspect_site(domain)
        policy_quality = analyze_policies(domain, live)
        experience = mine_experiences(osint.get("evidence", {}))
        policy_mismatches = detect_policy_mismatch(policy_quality, experience)
        risk = evaluate_risk(osint)

        try:
            ai_result = explain_trust(
                domain=domain,
                category=category,
                osint_data=osint,
                experience_data=experience,
                live_inspection=live,
                risk_result=risk
            )
        except Exception as ai_error:
            ai_result = {
                "analysis": (
                    "AI-based explanation is temporarily unavailable due to API limits. "
                    "The assessment is derived from OSINT, live inspection, "
                    "policy analysis, and experience patterns."
                ),
                "risk_level": risk["baseline_risk"]["risk_level"],
                "confidence": risk["baseline_risk"]["confidence"],
                "ai_error": str(ai_error)
            }

        infra = inspect_infrastructure(domain)
        security = analyze_security_posture(domain)
        content_meta = fingerprint_content(domain)

        trust_dimensions = evaluate_trust_dimensions(
            osint=osint,
            experience=experience,
            live=live,
            policy_quality=policy_quality,
            policy_mismatches=policy_mismatches,
            infra=infra,
            security=security,
            content=content_meta
        )

        return {
            "domain": domain,
            "category": category,
            "risk_level": ai_result["risk_level"],
            "confidence": ai_result["confidence"],
            "analysis": ai_result["analysis"],
            "osint": osint,
            "live": live,
            "experience": experience,
            "policy_quality": policy_quality,
            "policy_mismatches": policy_mismatches,
            "risk": risk,
            "trust_dimensions": trust_dimensions,
            "infra": infra,
            "security_posture": security,
            "content_fingerprint": content_meta
        }
    except Exception as e:
        return {"error": "Scan failed", "details": str(e)}

