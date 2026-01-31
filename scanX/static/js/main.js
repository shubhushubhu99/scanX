let globalOsint = null;

function startScan() {
  const url = document.getElementById("urlInput").value.trim();
  const category = document.getElementById("categoryInput").value;

  if (!url) {
    alert("Enter a domain");
    return;
  }

  fetch("/api/analyze", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ url, category })
  })
    .then(res => res.json())
    .then(data => {
      console.log("API RESPONSE:", data);

      if (data.error) {
        alert("Scan failed: " + (data.details || "Unknown error"));
        return;
      }

      render(data);
    })
    .catch(err => {
      console.error(err);
      alert("Network error");
    });
}

function render(data) {
  // SAFETY CHECK
  if (!data) return;
globalOsint = data.osint;

  /* =======================
     SHOW DASHBOARD
  ======================= */
  const dashboard = document.getElementById("dashboard");
  if (dashboard) dashboard.classList.remove("hidden");

  /* =======================
     VERDICT
  ======================= */
  const verdictEl = document.getElementById("riskLevel");
  const reasonEl = document.getElementById("riskReason");

  const baselineRisk =
    data.risk && data.risk.baseline_risk
      ? data.risk.baseline_risk
      : null;

  verdictEl.innerText = baselineRisk
    ? baselineRisk.risk_level
    : "Verdict unavailable";

  reasonEl.innerText = baselineRisk
    ? baselineRisk.reason
    : "Risk explanation unavailable.";

  /* =======================
     STRENGTHS
  ======================= */
  fillList("strengths", [
    data.live?.signals?.has_help_center && "Help center available",
    data.live?.signals?.has_refund_policy && "Refund policy present",
    data.live?.signals?.has_privacy_policy && "Privacy policy present",
    data.live?.signals?.has_terms && "Terms & conditions available"
  ]);

/* =======================
   KEY CONCERNS
======================= */
const concernsEl = document.getElementById("concerns");
concernsEl.innerHTML = "";

if (data.experience) {
  Object.entries(data.experience).forEach(([key, value]) => {
    if (value.count >= 3) {
      concernsEl.innerHTML += `
        <li>
          <strong>${key.replace(/_/g, " ")}</strong>
          (${value.count} mentions)
          <br />
          <button class="reference-btn"
            onclick="showReferences('${key}')">
            View references
          </button>
        </li>
      `;
    }
  });
}



  /* =======================
     EXPERIENCE BADGES
  ======================= */
  const badgesEl = document.getElementById("experienceBadges");
  badgesEl.innerHTML = "";

  if (data.experience) {
    Object.entries(data.experience).forEach(([k, v]) => {
      badgesEl.innerHTML += `
        <span class="badge">${k.replace(/_/g, " ")} (${v.count})</span>
      `;
    });
  }

  /* =======================
     OPERATIONAL SIGNALS
  ======================= */
  if (data.live?.signals) {
    fillList(
      "opsSignals",
      Object.entries(data.live.signals).map(
        ([k, v]) => `${k.replace(/_/g, " ")}: ${v ? "Yes" : "No"}`
      )
    );
  }

  /* =======================
     SOURCES
  ======================= */
  if (data.osint?.platforms_with_mentions) {
    fillList("sources", data.osint.platforms_with_mentions);
  }

  /* =======================
     POLICY MISMATCHES
  ======================= */
  const mismatchPanel = document.getElementById("policyMismatchPanel");
  const mismatchList = document.getElementById("policyMismatches");

  mismatchList.innerHTML = "";

  const mismatches = data.policy_mismatches || {};

  if (Object.keys(mismatches).length > 0) {
    Object.entries(mismatches).forEach(([key, value]) => {
      const cls =
        value.severity === "High"
          ? "policy-high"
          : value.severity === "Medium"
          ? "policy-medium"
          : "policy-low";

      mismatchList.innerHTML += `
        <li class="policy-item ${cls}">
          <strong>${key.toUpperCase()} POLICY:</strong>
          ${value.summary}
          <br />
          <small>Severity: ${value.severity}</small>
        </li>
      `;
    });

    mismatchPanel.classList.remove("hidden");
  } else {
    mismatchPanel.classList.add("hidden");
  }


  /* =======================
     TRUST DIMENSIONS
  ======================= */

  const trustPanel = document.getElementById("trustDimensionsPanel");
  const trustBox = document.getElementById("trustDimensions");

  trustBox.innerHTML = "";

  if (data.trust_dimensions) {
    Object.entries(data.trust_dimensions).forEach(([key, value]) => {
      const statusClass =
        "status-" + value.status.toLowerCase().replace(/\s+/g, "-");

      trustBox.innerHTML += `
        <div class="trust-row">
          <div class="trust-name">${key.replace(/_/g, " ")}</div>
          <div class="trust-status ${statusClass}">
            ${value.status}
          </div>
          <div class="trust-reason">
            ${value.reason}
          </div>
        </div>
      `;
    });

    trustPanel.classList.remove("hidden");
  } else {
    trustPanel.classList.add("hidden");
  }



  /* =======================
     AI EXPLANATION
  ======================= */
  document.getElementById("aiExplanation").innerText =
    data.analysis || "AI explanation unavailable.";
}

/* =======================
   HELPER
======================= */
function fillList(id, items) {
  const el = document.getElementById(id);
  if (!el || !items) return;

  el.innerHTML = "";
  items.filter(Boolean).forEach(item => {
    el.innerHTML += `<li>${item}</li>`;
  });
}

function showReferences(concernKey) {
  const modal = document.getElementById("referenceModal");
  const list = document.getElementById("modalLinks");
  const title = document.getElementById("modalTitle");

  list.innerHTML = "";
  title.innerText = `References for ${concernKey.replace(/_/g, " ")}`;

  if (!globalOsint || !globalOsint.evidence) {
    list.innerHTML = `<li>No reference data available.</li>`;
    modal.classList.remove("hidden");
    return;
  }

  const concernPlatformMap = {
    customer_support_issues: ["Quora", "Trustpilot", "Forums"],
    delivery_issues: ["Reddit", "Trustpilot", "Forums"],
    security_concerns: ["Security", "Reddit"],
    payment_issues: ["Trustpilot", "Forums"]
  };

  let found = false;
  const platforms = concernPlatformMap[concernKey] || [];

  // 1️⃣ Try mapped platforms first
  platforms.forEach(platform => {
    const items = globalOsint.evidence[platform] || [];
    items.forEach(item => {
      found = true;
      list.innerHTML += `
        <li>
          <a href="${item.link}" target="_blank">
            ${platform}: ${item.title || item.link}
          </a>
        </li>
      `;
    });
  });

  // 2️⃣ Fallback: show any available evidence
  if (!found) {
    Object.entries(globalOsint.evidence).forEach(([platform, items]) => {
      items.slice(0, 2).forEach(item => {
        list.innerHTML += `
          <li>
            <a href="${item.link}" target="_blank">
              ${platform}: ${item.title || item.link}
            </a>
          </li>
        `;
      });
    });
  }

  modal.classList.remove("hidden");
}


document.addEventListener("DOMContentLoaded", () => {
  const modal = document.getElementById("referenceModal");
  const closeBtn = document.getElementById("closeModalBtn");
  const overlay = modal.querySelector(".modal-overlay");

  closeBtn.addEventListener("click", () => {
    modal.classList.add("hidden");
  });

  overlay.addEventListener("click", () => {
    modal.classList.add("hidden");
  });
});
