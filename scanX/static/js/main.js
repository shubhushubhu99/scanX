function startScan() {
  const url = document.getElementById("urlInput").value.trim();
  const category = document.getElementById("categoryInput").value;

  if (!url) return alert("Enter a domain");

  fetch("/api/analyze", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ url, category })
  })
    .then(res => res.json())
    .then(data => render(data));
}

function render(data) {
  document.getElementById("dashboard").classList.remove("hidden");

  document.getElementById("riskLevel").innerText = data.risk_level;
  document.getElementById("riskReason").innerText =
    data.risk.baseline_risk.reason;

  fillList("strengths", [
    data.live.signals.has_help_center && "Help center available",
    data.live.signals.has_refund_policy && "Refund policy present",
    data.live.signals.has_privacy_policy && "Privacy policy present",
    data.live.signals.has_terms && "Terms & conditions available"
  ]);

  fillList("concerns",
    Object.entries(data.experience)
      .filter(([_, v]) => v.count >= 3)
      .map(([k]) => k.replace(/_/g, " ") + " frequently reported")
  );

  const badges = document.getElementById("experienceBadges");
  badges.innerHTML = "";
  Object.entries(data.experience).forEach(([k, v]) => {
    badges.innerHTML += `<span class="badge">${k.replace(/_/g," ")} (${v.count})</span>`;
  });

  fillList("opsSignals",
    Object.entries(data.live.signals)
      .map(([k, v]) => `${k.replace(/_/g," ")}: ${v ? "Yes" : "No"}`)
  );

  fillList("sources", data.osint.platforms_with_mentions);

  document.getElementById("aiExplanation").innerText = data.analysis;
}

function fillList(id, items) {
  const el = document.getElementById(id);
  el.innerHTML = "";
  items.filter(Boolean).forEach(i => el.innerHTML += `<li>${i}</li>`);
}
