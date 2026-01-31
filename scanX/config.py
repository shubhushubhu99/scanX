from core.reputation import collect_public_signals
from core.live_inspector import inspect_site
from core.experience_miner import mine_experiences
from core.risk_engine import evaluate_risk
from agents.deep_explainer import explain_trust

domain = "cgc.ac.in"
category = ""

osint = collect_public_signals(domain)
experience = mine_experiences(osint["evidence"])
live = inspect_site(domain)
risk = evaluate_risk(osint)

result = explain_trust(
    domain,
    category,
    osint,
    experience,
    live,
    risk
)

print(result["analysis"])
