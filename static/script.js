// ====================================
// TOXICITY DETECTION - SCRIPT.JS
// UPDATED: Side-by-side layout support
// ====================================

// Character count
const textInput = document.getElementById("textInput");
const charCount = document.getElementById("charCount");

textInput.addEventListener("input", () => {
  const count = textInput.value.length;
  charCount.textContent = `${count} characters`;
});

// Set example text
function setExample(text) {
  textInput.value = text;
  textInput.dispatchEvent(new Event("input"));
  textInput.focus();
}

// Analyze text
async function analyzeText() {
  const text = textInput.value.trim();

  if (!text) {
    showError("Please enter some text to analyze");
    return;
  }

  // Show loading
  document.getElementById("loading").style.display = "block";
  document.getElementById("results").style.display = "none";
  document.getElementById("errorMessage").style.display = "none";

  try {
    const response = await fetch("/api/analyze", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ text: text }),
    });

    const data = await response.json();

    if (data.error) {
      showError(data.error);
      return;
    }

    displayResults(data);
  } catch (error) {
    showError("An error occurred: " + error.message);
  } finally {
    document.getElementById("loading").style.display = "none";
  }
}

// ====================================
// DISPLAY RESULTS - UPDATED for HTML structure
// ====================================
function displayResults(data) {
  const results = document.getElementById("results");
  results.style.display = "block";

  // Status Banner
  const statusBanner = document.getElementById("statusBanner");
  statusBanner.className =
    "status-banner " + (data.is_toxic ? "toxic" : "safe");
  statusBanner.innerHTML = data.is_toxic
    ? '<i class="fas fa-exclamation-triangle"></i> TOXIC CONTENT DETECTED'
    : '<i class="fas fa-check-circle"></i> CONTENT IS SAFE';

  // ====================================
  // Display Original and Rewrite Text (Use HTML IDs)
  // ====================================
  const originalTextElem = document.getElementById("displayOriginalText");
  const rewriteTextElem = document.getElementById("displayRewriteText");

  if (originalTextElem) {
    originalTextElem.textContent = data.original_text;
  }

  if (rewriteTextElem) {
    rewriteTextElem.textContent =
      data.rewrite_suggestion ||
      "No toxic content detected. Original text is appropriate.";
  }

  // Toxicity Scores
  displayScores(data.toxicity_scores);

  // Flagged Categories
  displayFlaggedCategories(data.categories_flagged);

  // Scroll to results
  results.scrollIntoView({ behavior: "smooth", block: "start" });
}

// ====================================
// DISPLAY TOXICITY SCORES
// ====================================
function displayScores(scores) {
  const scoresContainer = document.getElementById("scoresContainer");
  const sortedScores = Object.entries(scores).sort((a, b) => b[1] - a[1]);

  let scoresHTML = "";
  sortedScores.forEach(([category, score]) => {
    const percentage = (score * 100).toFixed(2);
    const color = getScoreColor(score);
    const icon = getScoreIcon(score);

    scoresHTML += `
      <div class="score-item">
          <div class="score-header">
              <span class="score-label">${icon} ${category.replace(
      /_/g,
      " "
    )}</span>
              <span class="score-value" style="color: ${color}">${percentage}%</span>
          </div>
          <div class="score-bar">
              <div class="score-fill" style="width: ${percentage}%; background: ${color};"></div>
          </div>
      </div>
    `;
  });

  scoresContainer.innerHTML = scoresHTML;
}

// ====================================
// DISPLAY FLAGGED CATEGORIES
// ====================================
function displayFlaggedCategories(flagged) {
  const flaggedSection = document.getElementById("flaggedSection");

  if (flagged && flagged.length > 0) {
    flaggedSection.style.display = "block";

    let tagsHTML = "";
    flagged.forEach((cat) => {
      tagsHTML += `<span class="flagged-tag">${cat.replace(/_/g, " ")}</span>`;
    });

    flaggedSection.innerHTML = `
      <h3><i class="fas fa-flag"></i> Flagged Categories</h3>
      <div class="flagged-tags">${tagsHTML}</div>
    `;
  } else {
    flaggedSection.style.display = "none";
  }
}

// ====================================
// COPY AI SUGGESTION - UPDATED
// ====================================
function copySuggestion() {
  const suggestionText = document.getElementById("displayRewriteText");

  if (!suggestionText) {
    console.error("Suggestion text element not found");
    showError("Unable to copy suggestion");
    return;
  }

  const text = suggestionText.textContent;

  navigator.clipboard
    .writeText(text)
    .then(() => {
      // Show success message
      const btn = event.target.closest(".copy-suggestion-btn");
      if (btn) {
        const originalHTML = btn.innerHTML;
        btn.innerHTML = '<i class="fas fa-check"></i> Copied!';
        btn.style.background =
          "linear-gradient(135deg, #38ef7d 0%, #11998e 100%)";

        setTimeout(() => {
          btn.innerHTML = originalHTML;
          btn.style.background =
            "linear-gradient(135deg, #667eea 0%, #764ba2 100%)";
        }, 2000);
      }

      showSuccessMessage("✅ AI suggestion copied to clipboard!");
    })
    .catch((err) => {
      console.error("Failed to copy:", err);
      showError("Failed to copy text");
    });
}

// ====================================
// SHOW SUCCESS MESSAGE
// ====================================
function showSuccessMessage(message) {
  const successDiv = document.createElement("div");
  successDiv.className = "success-message";
  successDiv.innerHTML = `<i class="fas fa-check-circle"></i> ${message}`;
  document.body.appendChild(successDiv);

  setTimeout(() => {
    successDiv.classList.add("show");
  }, 100);

  setTimeout(() => {
    successDiv.classList.remove("show");
    setTimeout(() => successDiv.remove(), 400);
  }, 3000);
}

// ====================================
// HELPER FUNCTIONS
// ====================================
function getScoreColor(score) {
  if (score > 0.7) return "#ff6a00";
  if (score > 0.5) return "#f5576c";
  if (score > 0.3) return "#ffa726";
  return "#38ef7d";
}

function getScoreIcon(score) {
  if (score > 0.7) return '<i class="fas fa-times-circle"></i>';
  if (score > 0.5) return '<i class="fas fa-exclamation-triangle"></i>';
  if (score > 0.3) return '<i class="fas fa-exclamation-circle"></i>';
  return '<i class="fas fa-check-circle"></i>';
}

function escapeHtml(text) {
  const div = document.createElement("div");
  div.textContent = text;
  return div.innerHTML;
}

function showError(message) {
  const errorDiv = document.getElementById("errorMessage");
  errorDiv.innerHTML = `<i class="fas fa-exclamation-circle"></i> ${message}`;
  errorDiv.style.display = "block";
  document.getElementById("loading").style.display = "none";

  setTimeout(() => {
    errorDiv.style.display = "none";
  }, 5000);
}

function downloadReport() {
  // Get current results
  const results = document.getElementById("results");
  if (!results || results.style.display === "none") {
    showError("No results to download!");
    return;
  }

  // Create report text
  const originalText = textInput.value.trim();
  const timestamp = new Date().toLocaleString();

  let reportText = `
═══════════════════════════════════════════════════════════════
         TOXICITY DETECTION REPORT
═══════════════════════════════════════════════════════════════
Generated: ${timestamp}

ORIGINAL TEXT:
${originalText}

${document.getElementById("statusBanner").innerText}

TOXICITY SCORES:
${document.getElementById("scoresContainer").innerText}

${
  document.getElementById("flaggedSection").style.display !== "none"
    ? "FLAGGED CATEGORIES:\n" +
      document.getElementById("flaggedSection").innerText
    : ""
}

═══════════════════════════════════════════════════════════════
Report generated by Toxicity Detection System
═══════════════════════════════════════════════════════════════
  `;

  // Download as text file
  const blob = new Blob([reportText], { type: "text/plain" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `toxicity-report-${Date.now()}.txt`;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);

  showSuccessMessage("📥 Report downloaded successfully!");
}

function copyResults() {
  const resultsText = document.getElementById("results").innerText;
  navigator.clipboard
    .writeText(resultsText)
    .then(() => {
      showSuccessMessage("📋 Results copied to clipboard!");
    })
    .catch((err) => {
      showError("Failed to copy results");
    });
}

// ====================================
// KEYBOARD SHORTCUTS
// ====================================
// Enter key to analyze
textInput.addEventListener("keydown", (e) => {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    analyzeText();
  }
});

// Ctrl/Cmd + Enter to analyze
document.addEventListener("keydown", (e) => {
  if ((e.ctrlKey || e.metaKey) && e.key === "Enter") {
    e.preventDefault();
    analyzeText();
  }
});
