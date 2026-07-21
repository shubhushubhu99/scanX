let globalOsint = null;

const scanState = {
  isScanning: false,
  currentMode: null,
  logs: [],
  logIntervalId: null,
  progressIntervalId: null,
  progress: 0,
  startedAt: null,
};

function startScan(mode = "deep") {
  const url = document.getElementById("urlInput").value.trim();
  const category = document.getElementById("categoryInput").value;

  if (!url) {
    alert("Enter a domain");
    return;
  }

  if (scanState.isScanning) {
    // Prevent double clicks across Analyse / Deep Scan
    return;
  }

  scanState.isScanning = true;
  scanState.currentMode = mode;
  scanState.startedAt = Date.now();
  scanState.progress = 0;

  beginScanUI(mode);

  fetch("/api/analyze", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ url, category, mode })
  })
    .then(res => res.json())
    .then(data => {
      console.log("API RESPONSE:", data);

      if (data.error) {
        appendLog(
          `Scan failed: ${data.details || "Unknown error"}`,
          "error"
        );
        alert("Scan failed: " + (data.details || "Unknown error"));
        completeScanUI(false);
        return;
      }

      if (data.task_id) {
        pollTaskStatus(data.task_id);
      } else {
        render(data);
        completeScanUI(true, data);
      }
    })
    .catch(err => {
      console.error(err);
      appendLog("Network error while calling /api/analyze", "error");
      alert("Network error");
      completeScanUI(false);
    });
}

/* =======================
   RISK LEVEL -> CSS CLASS
function getRiskClass(riskLevelText) {
  const level = (riskLevelText || "").toLowerCase();

  if (level.includes("low")) {
    return "risk-low";
  }
  if (level.includes("moderate") || level.includes("medium")) {
    return "risk-moderate";
  }
  if (level.includes("high")) {
    return "risk-high";
  }
  return null;
}

function render(data) {
  // SAFETY CHECK
  if (!data) return;
  globalOsint = data.osint;
  window.currentTrustDimensions = data.trust_dimensions;

  /* =======================
     SHOW DASHBOARD
  ======================= */
  const dashboard = document.getElementById("dashboard");
  if (dashboard) dashboard.classList.remove("hidden");

  const scanMeta = document.getElementById("scanMeta");
  if (scanMeta) scanMeta.classList.remove("hidden");

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

  // Apply color coding to the verdict card based on risk level
  const verdictCard = verdictEl.closest(".verdict");
  if (verdictCard) {
    verdictCard.classList.remove("risk-low", "risk-moderate", "risk-high");

    const riskClass = getRiskClass(baselineRisk ? baselineRisk.risk_level : "");
    if (riskClass) {
      verdictCard.classList.add(riskClass);
    }
  }

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
  let concernCount = 0;

  if (data.experience) {
    Object.entries(data.experience).forEach(([key, value]) => {
      if (value.count >= 3) {
        concernCount += 1;
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
     META STATS
  ======================= */
  const statTotalItems = document.getElementById("statTotalItems");
  const statDetections = document.getElementById("statDetections");
  const statDuration = document.getElementById("statDuration");

  let totalSignals = 0;

  if (data.experience) {
    totalSignals += Object.values(data.experience).reduce(
      (sum, v) => sum + (v.count || 0),
      0
    );
  }

  if (data.live?.signals) {
    totalSignals += Object.keys(data.live.signals).length;
  }

  if (data.osint?.platforms_with_mentions) {
    totalSignals += data.osint.platforms_with_mentions.length;
  }

  if (statTotalItems) {
    statTotalItems.innerText = totalSignals.toString();
  }
  if (statDetections) {
    statDetections.innerText = concernCount.toString();
  }
  if (statDuration) {
    const elapsedMs = scanState.startedAt
      ? Date.now() - scanState.startedAt
      : 0;
    const seconds = Math.max(0.5, elapsedMs / 1000);
    statDuration.innerText = `${seconds.toFixed(1)}s`;
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
    <div class="trust-row clickable"
       data-dimension="${key}"
       data-status="${value.status}"
       onclick="handleDimensionClick(this)">
    <div class="trust-name">${key.replace(/_/g, " ")}</div>
    <div class="trust-status ${statusClass}">${value.status}</div>
    <div class="trust-reason">${value.reason}</div>
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
   NEW SCAN / RESET
======================= */
function resetScan() {
  // Don't reset mid-scan
  if (scanState.isScanning) {
    return;
  }

  // Hide dashboard + scan meta
  const dashboard = document.getElementById("dashboard");
  if (dashboard) dashboard.classList.add("hidden");

  const scanMeta = document.getElementById("scanMeta");
  if (scanMeta) scanMeta.classList.add("hidden");

  // Clear verdict
  const verdictEl = document.getElementById("riskLevel");
  const reasonEl = document.getElementById("riskReason");
  if (verdictEl) verdictEl.innerText = "";
  if (reasonEl) reasonEl.innerText = "";

  const verdictCard = verdictEl ? verdictEl.closest(".verdict") : null;
  if (verdictCard) {
    verdictCard.classList.remove("risk-low", "risk-moderate", "risk-high");
  }

  // Clear lists and badges
  ["strengths", "concerns", "opsSignals", "sources", "experienceBadges", "policyMismatches", "trustDimensions"]
    .forEach((id) => {
      const el = document.getElementById(id);
      if (el) el.innerHTML = "";
    });

  // Hide conditional panels
  document.getElementById("policyMismatchPanel")?.classList.add("hidden");
  document.getElementById("trustDimensionsPanel")?.classList.add("hidden");

  // Reset stats
  const statTotalItems = document.getElementById("statTotalItems");
  const statDetections = document.getElementById("statDetections");
  const statDuration = document.getElementById("statDuration");
  if (statTotalItems) statTotalItems.innerText = "0";
  if (statDetections) statDetections.innerText = "0";
  if (statDuration) statDuration.innerText = "0.0s";

  // Reset progress bar
  const progressFill = document.getElementById("progressFill");
  const progressPercent = document.getElementById("progressPercent");
  if (progressFill) {
    progressFill.style.width = "0%";
    progressFill.classList.remove("is-animating");
  }
  if (progressPercent) progressPercent.innerText = "0%";

  // Clear AI explanation
  const aiExplanation = document.getElementById("aiExplanation");
  if (aiExplanation) aiExplanation.innerText = "";

  // Clear logs
  scanState.logs = [];
  const logList = document.getElementById("logList");
  if (logList) logList.innerHTML = "";
  document.getElementById("logPanel")?.classList.add("collapsed");

  // Reset buttons in case any leftover state
  const analyzeBtn = document.getElementById("analyzeBtn");
  const deepBtn = document.getElementById("deepScanBtn");
  [analyzeBtn, deepBtn].filter(Boolean).forEach((btn) => {
    btn.disabled = false;
    btn.classList.remove("is-loading", "is-success");
    if (btn.dataset.originalLabel) {
      btn.innerText = btn.dataset.originalLabel;
    }
  });

  // Clear + refocus URL input
  const urlInput = document.getElementById("urlInput");
  if (urlInput) {
    urlInput.value = "";
    urlInput.focus();
  }

  // Scroll back to the input section
  const inputSection = document.querySelector(".input-section") || document.getElementById("urlInput");
  if (inputSection) {
    inputSection.scrollIntoView({ behavior: "smooth", block: "start" });
  }

  globalOsint = null;
  window.currentTrustDimensions = null;

  appendLog("Ready for a new scan.", "info");
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

/* =======================
   LOGGING & PROGRESS
======================= */

function appendLog(message, level = "info") {
  const logList = document.getElementById("logList");
  if (!logList) return;

  const now = new Date();
  const timestamp = now.toLocaleTimeString(undefined, {
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
  });

  const entry = {
    id: `${now.getTime()}-${Math.random().toString(16).slice(2)}`,
    timestamp,
    level,
    message,
  };

  scanState.logs.push(entry);

  const row = document.createElement("div");
  row.className = `log-entry ${level}`;

  const iconMap = {
    info: "⧉",
    success: "✔",
    warning: "⚠",
    error: "⨯",
  };

  const statusLabelMap = {
    info: "Info",
    success: "Success",
    warning: "Warning",
    error: "Error",
  };

  row.innerHTML = `
    <div class="log-meta">
      <span class="log-time">${entry.timestamp}</span>
      <span class="log-status">${statusLabelMap[level] || "Info"}</span>
    </div>
    <div class="log-message">
      <span class="log-icon">${iconMap[level] || "⧉"}</span>
      ${entry.message}
    </div>
  `;

  logList.appendChild(row);

  const container = document.querySelector(".log-body");
  if (container) {
    container.scrollTop = container.scrollHeight;
  }
}

function toggleLiveLog(enabled) {
  const panel = document.getElementById("logPanel");
  if (!panel) return;

  if (enabled) {
    panel.classList.remove("collapsed");
  } else {
    panel.classList.add("collapsed");
  }
}

function downloadLogs() {
  if (!scanState.logs.length) {
    alert("No logs available yet.");
    return;
  }

  const lines = scanState.logs.map(
    (l) => `[${l.timestamp}] [${l.level.toUpperCase()}] ${l.message}`
  );

  const blob = new Blob([lines.join("\n")], { type: "text/plain" });
  const url = URL.createObjectURL(blob);

  const a = document.createElement("a");
  a.href = url;
  a.download = `scanx-logs-${new Date()
    .toISOString()
    .replace(/[:.]/g, "-")}.txt`;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}

function beginScanUI(mode) {
  const analyzeBtn = document.getElementById("analyzeBtn");
  const deepBtn = document.getElementById("deepScanBtn");
  const progressFill = document.getElementById("progressFill");
  const progressPercent = document.getElementById("progressPercent");

  if (analyzeBtn) {
    analyzeBtn.disabled = true;
    analyzeBtn.classList.remove("is-success");
  }
  if (deepBtn) {
    deepBtn.disabled = true;
    deepBtn.classList.remove("is-success");
  }

  const targetBtn = mode === "analyze" ? analyzeBtn : deepBtn;
  if (targetBtn) {
    if (!targetBtn.dataset.originalLabel) {
      targetBtn.dataset.originalLabel = targetBtn.innerText.trim();
    }

    const loadingLabel =
      mode === "analyze" ? "Analyzing…" : "Deep scanning…";

    targetBtn.classList.add("is-loading");
    targetBtn.innerHTML = `
      <span class="btn-spinner"></span>
      <span>${loadingLabel}</span>
    `;
  }

  if (progressFill) {
    progressFill.style.width = "0%";
    progressFill.classList.add("is-animating");
  }
  if (progressPercent) {
    progressPercent.innerText = "0%";
  }

  const newScanBtn = document.getElementById("newScanBtn");
  if (newScanBtn) newScanBtn.classList.add("hidden");

  // Reset and optionally open logs
  scanState.logs = [];
  const logList = document.getElementById("logList");
  if (logList) logList.innerHTML = "";

  const logToggle = document.getElementById("logToggle");
  if (logToggle && logToggle.checked) {
    toggleLiveLog(true);
  }

  // Simulated live logs while request is in flight
  const steps =
    mode === "analyze"
      ? [
        "Initializing lightweight trust checks",
        "Collecting surface OSINT signals",
        "Evaluating basic risk posture",
        "Summarizing high-level verdict",
      ]
      : [
        "Bootstrapping deep scan pipeline",
        "Enumerating OSINT and infra sources",
        "Inspecting content, policy and UX signals",
        "Running risk engine across trust dimensions",
        "Aggregating AI explanation and references",
      ];

  let stepIndex = 0;
  scanState.logIntervalId = window.setInterval(() => {
    if (!scanState.isScanning || stepIndex >= steps.length) {
      window.clearInterval(scanState.logIntervalId);
      scanState.logIntervalId = null;
      return;
    }
    appendLog(steps[stepIndex], "info");
    stepIndex += 1;
  }, 900);

  // Progress animation up to ~80% until we complete
  scanState.progress = 0;
  scanState.progressIntervalId = window.setInterval(() => {
    if (!scanState.isScanning) {
      window.clearInterval(scanState.progressIntervalId);
      scanState.progressIntervalId = null;
      return;
    }
    const maxWhileRunning = 80;
    const increment = Math.random() * 6 + 4; // 4–10%
    scanState.progress = Math.min(
      maxWhileRunning,
      scanState.progress + increment
    );

    if (progressFill) {
      progressFill.style.width = `${scanState.progress}%`;
    }
    if (progressPercent) {
      progressPercent.innerText = `${Math.round(
        scanState.progress
      )}%`;
    }
  }, 700);
}

function completeScanUI(success, data) {
  scanState.isScanning = false;

  if (scanState.logIntervalId) {
    window.clearInterval(scanState.logIntervalId);
    scanState.logIntervalId = null;
  }
  if (scanState.progressIntervalId) {
    window.clearInterval(scanState.progressIntervalId);
    scanState.progressIntervalId = null;
  }

  const analyzeBtn = document.getElementById("analyzeBtn");
  const deepBtn = document.getElementById("deepScanBtn");
  const progressFill = document.getElementById("progressFill");
  const progressPercent = document.getElementById("progressPercent");

  const allBtns = [analyzeBtn, deepBtn].filter(Boolean);
  allBtns.forEach((btn) => {
    btn.disabled = false;
    btn.classList.remove("is-loading");
  });

  if (progressFill) {
    progressFill.classList.remove("is-animating");
    progressFill.style.width = success ? "100%" : `${Math.max(
      scanState.progress,
      15
    )}%`;
  }
  if (progressPercent) {
    progressPercent.innerText = success ? "100%" : `${Math.round(
      scanState.progress
    )}%`;
  }

  if (success) {
    const mode = scanState.currentMode || "deep";
    const targetBtn = mode === "analyze" ? analyzeBtn : deepBtn;

    if (targetBtn) {
      const original = targetBtn.dataset.originalLabel || "Scan";
      targetBtn.classList.add("is-success");
      targetBtn.innerHTML = `
        <span class="btn-checkmark">✓</span>
        <span>${original}</span>
      `;

      window.setTimeout(() => {
        targetBtn.classList.remove("is-success");
        targetBtn.innerText = original;
      }, 900);
    }

    appendLog("Scan completed successfully.", "success");
  } else {
    appendLog("Scan ended with an error.", "error");
  }

  const newScanBtn = document.getElementById("newScanBtn");
  if (newScanBtn) newScanBtn.classList.remove("hidden");
}

function explainTrustDimension(dimension, status, signals) {
  fetch("/api/explain-dimension", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      dimension,
      status,
      signals
    })
  })
    .then(res => res.json())
    .then(data => {
      document.getElementById("dimensionModalTitle").innerText =
        dimension.replace(/_/g, " ");

      document.getElementById("dimensionModalBody").innerText =
        data.explanation;

      const badge = document.getElementById("dimensionStatus");
      badge.innerText = status;
      badge.className = "status-badge " + status.toLowerCase();

      document.getElementById("dimensionModal")
        .classList.remove("hidden");
    });

}


function closeDimensionModal() {
  document.getElementById("dimensionModal").classList.add("hidden");
}

function handleDimensionClick(el) {
  const dimension = el.dataset.dimension;
  const status = el.dataset.status;

  // Find matching trust dimension data
  const signals = window.currentTrustDimensions
    ? window.currentTrustDimensions[dimension]
    : {};

  explainTrustDimension(dimension, status, signals);
}

function closeDimensionModal() {
  document.getElementById("dimensionModal").classList.add("hidden");
}