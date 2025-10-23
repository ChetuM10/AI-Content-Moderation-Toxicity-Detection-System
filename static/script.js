// ====================================
// TOXICITY DETECTION - COMPLETE SYSTEM
// With Authentication, History, Favorites
// Version: 2.1 - FIXED TOKEN ISSUE
// ====================================

// ====================================
// AUTHENTICATION STATE MANAGEMENT
// ====================================
let currentUser = null;
let authToken = null;
let currentRecordId = null;

// Initialize app on page load
document.addEventListener("DOMContentLoaded", () => {
  console.log("✅ Toxicity Detection System v2.1 loaded");
  checkAuthStatus();
  initializeFileUpload();
});

// ====================================
// AUTH STATUS CHECK
// ====================================
function checkAuthStatus() {
  const token = localStorage.getItem("token"); // ← FIXED: Use "token" not "authToken"
  const userEmail = localStorage.getItem("userEmail");

  if (token && userEmail) {
    authToken = token;
    currentUser = { email: userEmail };
    updateUIForLoggedInUser();
    console.log("✅ User logged in:", currentUser.email);
    console.log("✅ Token found:", authToken ? "YES" : "NO");
  } else {
    authToken = null;
    currentUser = null;
    updateUIForGuestUser();
    console.log("👤 Guest user mode");
  }
}

function updateUIForLoggedInUser() {
  // Show user menu, hide guest menu
  const guestMenu = document.getElementById("guestMenu");
  const userMenu = document.getElementById("userMenu");
  const userName = document.getElementById("userName");

  if (guestMenu) guestMenu.style.display = "none";
  if (userMenu) userMenu.style.display = "flex";
  if (userName) userName.textContent = currentUser.email.split("@")[0];

  // Hide login reminder
  const loginReminder = document.getElementById("loginReminder");
  if (loginReminder) loginReminder.style.display = "none";

  // Show favorite button if results are visible
  const results = document.getElementById("results");
  if (results && results.style.display !== "none") {
    const favoriteBtn = document.getElementById("favoriteBtn");
    if (favoriteBtn) favoriteBtn.style.display = "inline-flex";
  }
}

function updateUIForGuestUser() {
  // Show guest menu, hide user menu
  const guestMenu = document.getElementById("guestMenu");
  const userMenu = document.getElementById("userMenu");

  if (guestMenu) guestMenu.style.display = "flex";
  if (userMenu) userMenu.style.display = "none";

  // Show login reminder
  const loginReminder = document.getElementById("loginReminder");
  if (loginReminder) loginReminder.style.display = "flex";

  // Hide favorite button
  const favoriteBtn = document.getElementById("favoriteBtn");
  if (favoriteBtn) favoriteBtn.style.display = "none";
}

// ====================================
// AUTHENTICATION API CALLS
// ====================================
async function apiCall(endpoint, method = "GET", body = null) {
  const options = {
    method,
    headers: {
      "Content-Type": "application/json",
    },
  };

  // Add auth token if available
  if (authToken) {
    options.headers["Authorization"] = `Bearer ${authToken}`;
    console.log(`🔑 Sending request to ${endpoint} with token`);
  } else {
    console.log(`🔓 Sending request to ${endpoint} WITHOUT token`);
  }

  if (body) {
    options.body = JSON.stringify(body);
  }

  const response = await fetch(endpoint, options);

  // Handle non-JSON responses
  let data;
  try {
    data = await response.json();
  } catch (e) {
    data = { error: "Invalid server response" };
  }

  if (!response.ok) {
    // Handle token expiration
    if (response.status === 401 && authToken) {
      console.warn("⚠️ Token expired or invalid, logging out...");
      logout();
      showError("Session expired. Please login again.");
    }
    throw new Error(data.error || data.message || "Request failed");
  }

  return data;
}

// ====================================
// MODAL CONTROLS
// ====================================
function openLoginModal() {
  const modal = document.getElementById("loginModal");
  if (modal) modal.style.display = "flex";
}

function closeLoginModal() {
  const modal = document.getElementById("loginModal");
  const form = document.getElementById("loginForm");
  if (modal) modal.style.display = "none";
  if (form) form.reset();

  // Remove any error messages
  const errorMsg = form?.querySelector(".modal-error-message");
  if (errorMsg) errorMsg.remove();
}

function openRegisterModal() {
  const modal = document.getElementById("registerModal");
  if (modal) modal.style.display = "flex";
}

function closeRegisterModal() {
  const modal = document.getElementById("registerModal");
  const form = document.getElementById("registerForm");
  if (modal) modal.style.display = "none";
  if (form) form.reset();

  // Remove any error messages
  const errorMsg = form?.querySelector(".modal-error-message");
  if (errorMsg) errorMsg.remove();
}

function switchToRegister() {
  closeLoginModal();
  openRegisterModal();
}

function switchToLogin() {
  closeRegisterModal();
  openLoginModal();
}

// ====================================
// LOGIN HANDLER
// ====================================
async function handleLogin(event) {
  event.preventDefault();

  const email = document.getElementById("loginEmail").value;
  const password = document.getElementById("loginPassword").value;

  // Disable submit button during login
  const submitBtn = event.target.querySelector('button[type="submit"]');
  const originalText = submitBtn.innerHTML;
  submitBtn.disabled = true;
  submitBtn.innerHTML =
    '<i class="fas fa-spinner fa-spin"></i> <span>Logging in...</span>';

  try {
    const data = await apiCall("/api/auth/login", "POST", { email, password });

    // Store token and user info - FIXED: Use "token" key consistently
    localStorage.setItem("token", data.access_token);
    localStorage.setItem("userEmail", email);
    authToken = data.access_token;
    currentUser = { email };

    console.log("✅ Login successful! Token saved:", authToken ? "YES" : "NO");

    // Update UI
    updateUIForLoggedInUser();
    closeLoginModal();
    showSuccessMessage("✅ Login successful! Welcome back!");
  } catch (error) {
    // Display error in modal
    showModalError("loginForm", "Invalid email or password. Please try again.");
    console.error("Login error:", error);
  } finally {
    // Re-enable button
    submitBtn.disabled = false;
    submitBtn.innerHTML = originalText;
  }
}

// ====================================
// REGISTER HANDLER
// ====================================
async function handleRegister(event) {
  event.preventDefault();

  const email = document.getElementById("registerEmail").value;
  const password = document.getElementById("registerPassword").value;
  const confirmPassword = document.getElementById(
    "registerPasswordConfirm"
  ).value;

  // Validate passwords match
  if (password !== confirmPassword) {
    showModalError("registerForm", "Passwords do not match");
    return;
  }

  // Validate password length
  if (password.length < 8) {
    showModalError("registerForm", "Password must be at least 8 characters");
    return;
  }

  // Disable submit button during registration
  const submitBtn = event.target.querySelector('button[type="submit"]');
  const originalText = submitBtn.innerHTML;
  submitBtn.disabled = true;
  submitBtn.innerHTML =
    '<i class="fas fa-spinner fa-spin"></i> <span>Creating account...</span>';

  try {
    await apiCall("/api/auth/register", "POST", { email, password });

    closeRegisterModal();
    showSuccessMessage("✅ Account created! Please login.");

    // Auto-open login modal
    setTimeout(() => {
      openLoginModal();
      const loginEmail = document.getElementById("loginEmail");
      if (loginEmail) loginEmail.value = email;
    }, 1500);
  } catch (error) {
    // Display error in modal
    showModalError(
      "registerForm",
      error.message || "Registration failed. Please try again."
    );
    console.error("Registration error:", error);
  } finally {
    // Re-enable button
    submitBtn.disabled = false;
    submitBtn.innerHTML = originalText;
  }
}

// ====================================
// SHOW ERROR IN MODAL
// ====================================
function showModalError(formId, message) {
  const form = document.getElementById(formId);
  if (!form) return;

  // Remove existing error if present
  const existingError = form.querySelector(".modal-error-message");
  if (existingError) {
    existingError.remove();
  }

  // Create error message element
  const errorDiv = document.createElement("div");
  errorDiv.className = "modal-error-message";
  errorDiv.innerHTML = `<i class="fas fa-exclamation-triangle"></i> ${message}`;

  // Insert at the top of the form
  form.insertBefore(errorDiv, form.firstChild);

  // Shake animation
  errorDiv.style.animation = "shake 0.5s ease";

  // Auto-remove after 5 seconds
  setTimeout(() => {
    errorDiv.style.opacity = "0";
    setTimeout(() => errorDiv.remove(), 300);
  }, 5000);
}

// ====================================
// LOGOUT HANDLER
// ====================================
function logout() {
  if (!confirm("Are you sure you want to logout?")) return;

  localStorage.removeItem("token"); // ← FIXED: Use "token" not "authToken"
  localStorage.removeItem("userEmail");
  authToken = null;
  currentUser = null;

  updateUIForGuestUser();
  showSuccessMessage("👋 Logged out successfully");

  // Close history panel if open
  const historyPanel = document.getElementById("historyPanel");
  if (historyPanel) historyPanel.classList.remove("active");

  // Clear current results
  const results = document.getElementById("results");
  if (results) results.style.display = "none";
}

// ====================================
// CHARACTER COUNT
// ====================================
const textInput = document.getElementById("textInput");
const charCount = document.getElementById("charCount");

if (textInput && charCount) {
  textInput.addEventListener("input", () => {
    const count = textInput.value.length;
    charCount.textContent = `${count} characters`;
  });
}

// ====================================
// SET EXAMPLE TEXT
// ====================================
function setExample(text) {
  if (textInput) {
    textInput.value = text;
    textInput.dispatchEvent(new Event("input"));
    textInput.focus();
  }
}

// ====================================
// ANALYZE TEXT
// ====================================
async function analyzeText() {
  const text = textInput.value.trim();

  if (!text) {
    showError("Please enter some text to analyze");
    return;
  }

  // Check authentication status before analyzing
  checkAuthStatus();

  console.log("🔍 Starting analysis...");
  console.log("👤 User:", currentUser ? currentUser.email : "Guest");
  console.log("🔑 Token:", authToken ? "Present" : "Missing");

  // Show loading
  document.getElementById("loading").style.display = "block";
  document.getElementById("results").style.display = "none";
  document.getElementById("errorMessage").style.display = "none";

  try {
    const data = await apiCall("/api/analyze", "POST", { text });

    console.log("✅ Analysis complete!");
    console.log("📝 Record ID:", data.record_id);

    // Store record ID for favorites
    currentRecordId = data.record_id;

    displayResults(data);

    // Show success message if logged in and history saved
    if (authToken && data.record_id) {
      showSuccessMessage("✅ Analysis complete! Saved to history.");
    }
  } catch (error) {
    showError("An error occurred: " + error.message);
    console.error("Analysis error:", error);
  } finally {
    document.getElementById("loading").style.display = "none";
  }
}

// ====================================
// DISPLAY RESULTS
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

  // Display Original and Rewrite Text
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

  // Display Sentiment Analysis
  if (data.sentiment_original && data.sentiment_cleaned) {
    displaySentiment(data.sentiment_original, data.sentiment_cleaned);
  }

  // Toxicity Scores
  if (data.toxicity_scores) {
    displayScores(data.toxicity_scores);
  }

  // Flagged Categories
  if (data.categories_flagged) {
    displayFlaggedCategories(data.categories_flagged);
  }

  // Display toxic words if found
  if (data.toxic_words_found && data.toxic_words_found.length > 0) {
    displayToxicWords(data.toxic_words_found);
  }

  // Show favorite button if logged in
  if (authToken && currentRecordId) {
    const favoriteBtn = document.getElementById("favoriteBtn");
    if (favoriteBtn) favoriteBtn.style.display = "inline-flex";
  }

  // Scroll to results
  results.scrollIntoView({ behavior: "smooth", block: "start" });
}

// ====================================
// DISPLAY SENTIMENT ANALYSIS
// ====================================
function displaySentiment(original, cleaned) {
  const sentimentSection = document.getElementById("sentimentSection");

  if (!sentimentSection) {
    console.warn("Sentiment section not found in HTML");
    return;
  }

  sentimentSection.style.display = "block";

  let sentimentHTML = `
    <h3><i class="fas fa-smile"></i> Sentiment Analysis</h3>
    <div class="sentiment-cards">
      <div class="sentiment-card">
        <div class="sentiment-header">
          <span class="sentiment-label">Original Text</span>
          <span class="sentiment-emoji" style="font-size: 2rem;">${
            original.emoji
          }</span>
        </div>
        <div class="sentiment-body">
          <p class="sentiment-result" style="color: ${original.color}">
            <strong>${original.label}</strong>
          </p>
          <div class="sentiment-details">
            <div class="sentiment-metric">
              <span>Polarity:</span>
              <span>${original.polarity.toFixed(2)}</span>
            </div>
            <div class="sentiment-metric">
              <span>Confidence:</span>
              <span>${original.confidence.toFixed(1)}%</span>
            </div>
          </div>
        </div>
      </div>
  `;

  // Only show cleaned sentiment if different
  if (
    cleaned.label !== original.label ||
    Math.abs(cleaned.polarity - original.polarity) > 0.1
  ) {
    sentimentHTML += `
      <div class="sentiment-card">
        <div class="sentiment-header">
          <span class="sentiment-label">After Cleaning</span>
          <span class="sentiment-emoji" style="font-size: 2rem;">${
            cleaned.emoji
          }</span>
        </div>
        <div class="sentiment-body">
          <p class="sentiment-result" style="color: ${cleaned.color}">
            <strong>${cleaned.label}</strong>
          </p>
          <div class="sentiment-details">
            <div class="sentiment-metric">
              <span>Polarity:</span>
              <span>${cleaned.polarity.toFixed(2)}</span>
            </div>
            <div class="sentiment-metric">
              <span>Confidence:</span>
              <span>${cleaned.confidence.toFixed(1)}%</span>
            </div>
          </div>
        </div>
      </div>
    `;
  }

  sentimentHTML += `</div>`;
  sentimentSection.innerHTML = sentimentHTML;
}

// ====================================
// DISPLAY TOXICITY SCORES
// ====================================
function displayScores(scores) {
  const scoresContainer = document.getElementById("scoresContainer");

  if (!scoresContainer) {
    console.warn("Scores container not found");
    return;
  }

  const sortedScores = Object.entries(scores).sort((a, b) => b[1] - a[1]);

  let scoresHTML = "";
  sortedScores.forEach(([category, score]) => {
    const percentage = (score * 100).toFixed(2);
    const color = getScoreColor(score);
    const icon = getScoreIcon(score);

    scoresHTML += `
      <div class="score-item">
        <div class="score-header">
          <span class="score-label">${icon} ${formatCategoryName(
      category
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

  if (!flaggedSection) return;

  if (flagged && flagged.length > 0) {
    flaggedSection.style.display = "block";

    let tagsHTML = "";
    flagged.forEach((cat) => {
      tagsHTML += `<span class="flagged-tag">${formatCategoryName(cat)}</span>`;
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
// DISPLAY TOXIC WORDS
// ====================================
function displayToxicWords(words) {
  const toxicWordsSection = document.getElementById("toxicWordsSection");

  if (!toxicWordsSection) return;

  if (words && words.length > 0) {
    toxicWordsSection.style.display = "block";

    let wordsHTML = "";
    words.forEach((word) => {
      wordsHTML += `<span class="toxic-word-badge">${escapeHtml(word)}</span>`;
    });

    toxicWordsSection.innerHTML = `
      <h3><i class="fas fa-exclamation-circle"></i> Detected Toxic Words</h3>
      <div class="toxic-words-container">${wordsHTML}</div>
      <p class="toxic-words-note">These words were replaced with [REDACTED] in the cleaned text.</p>
    `;
  } else {
    toxicWordsSection.style.display = "none";
  }
}

// ====================================
// COPY SUGGESTION
// ====================================
function copySuggestion() {
  const suggestionText = document.getElementById("displayRewriteText");

  if (!suggestionText) {
    showError("Unable to copy suggestion");
    return;
  }

  const text = suggestionText.textContent;

  navigator.clipboard
    .writeText(text)
    .then(() => {
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
// HISTORY PANEL
// ====================================
async function toggleHistory() {
  const historyPanel = document.getElementById("historyPanel");

  if (!historyPanel) {
    console.error("History panel element not found in HTML");
    showError("History panel not found. Please refresh the page.");
    return;
  }

  if (!authToken) {
    showError("Please login to view history");
    openLoginModal();
    return;
  }

  historyPanel.classList.toggle("active");

  // Load history only if panel is now visible
  if (historyPanel.classList.contains("active")) {
    await loadHistory();
  }
}

async function loadHistory(filter = "all") {
  const historyContent = document.getElementById("historyContent");

  if (!historyContent) {
    console.error("History content element not found");
    return;
  }

  historyContent.innerHTML =
    '<div class="history-loading"><div class="spinner"></div><p>Loading history...</p></div>';

  try {
    console.log("Fetching history with filter:", filter);

    let url = "/api/history";
    if (filter !== "all") {
      url += `?filter=${filter}`;
    }

    const data = await apiCall(url);

    console.log("History data received:", data);

    if (data.history && data.history.length > 0) {
      displayHistoryRecords(data.history);
    } else {
      historyContent.innerHTML = `
        <div style="text-align: center; padding: 60px 20px;">
          <i class="fas fa-history" style="font-size: 4rem; color: var(--text-secondary); opacity: 0.3;"></i>
          <p style="color: var(--text-secondary); margin-top: 20px; font-size: 1.1rem;">No analysis history yet</p>
          <p style="color: var(--text-secondary); margin-top: 10px; font-size: 0.9rem;">Start analyzing text to build your history!</p>
        </div>
      `;
    }
  } catch (error) {
    console.error("Failed to load history:", error);
    historyContent.innerHTML = `
      <div style="text-align: center; padding: 40px 20px;">
        <i class="fas fa-exclamation-triangle" style="font-size: 3rem; color: var(--toxic);"></i>
        <p style="color: var(--toxic); margin-top: 20px;">Failed to load history</p>
        <p style="color: var(--text-secondary); margin-top: 10px; font-size: 0.9rem;">${error.message}</p>
        <button onclick="loadHistory()" style="margin-top: 20px; padding: 10px 20px; background: var(--gold); color: var(--bg-dark); border: none; border-radius: 8px; cursor: pointer; font-weight: 600;">
          <i class="fas fa-redo"></i> Retry
        </button>
      </div>
    `;
  }
}

function displayHistoryRecords(records) {
  const historyContent = document.getElementById("historyContent");

  if (!historyContent) return;

  let html = "";
  records.forEach((record) => {
    // Fix date parsing - use created_at or timestamp
    const dateStr = record.created_at || record.timestamp;
    const date = dateStr
      ? new Date(dateStr).toLocaleDateString()
      : "Unknown Date";
    const time = dateStr
      ? new Date(dateStr).toLocaleTimeString()
      : "Unknown Time";
    const recordId = record._id || record.id;

    html += `
      <div class="history-item" onclick="loadHistoryRecord('${recordId}')">
        <div class="history-item-header">
          <span class="history-status ${record.is_toxic ? "toxic" : "safe"}">
            ${record.is_toxic ? "⚠️ Toxic" : "✅ Safe"}
          </span>
          <span>${date}</span>
        </div>
        <p class="history-text">${escapeHtml(record.original_text)}</p>
        <div class="history-meta">
          <span>${time}</span>
          <div class="history-actions">
            <button class="history-action-btn ${
              record.is_favorite || record.favorite ? "favorited" : ""
            }" 
                    onclick="event.stopPropagation(); toggleHistoryFavorite('${recordId}', this)"
                    title="Toggle favorite">
              <i class="fas fa-star"></i>
            </button>
            <button class="history-action-btn" 
                    onclick="event.stopPropagation(); deleteHistoryRecord('${recordId}')"
                    title="Delete record">
              <i class="fas fa-trash"></i>
            </button>
          </div>
        </div>
      </div>
    `;
  });

  historyContent.innerHTML = html;
}

async function loadHistoryRecord(recordId) {
  console.log("Loading record:", recordId);
  showSuccessMessage("Loading analysis record...");

  try {
    const data = await apiCall(`/api/history/${recordId}`);

    console.log("Record data received:", data);

    // Populate the text input with the historical text
    textInput.value = data.original_text;
    textInput.dispatchEvent(new Event("input"));

    // Display the results - the backend now returns the COMPLETE record
    displayResults(data);

    // Close history panel
    const historyPanel = document.getElementById("historyPanel");
    if (historyPanel) historyPanel.classList.remove("active");

    // Scroll to results
    document.getElementById("results").scrollIntoView({ behavior: "smooth" });
  } catch (error) {
    showError("Failed to load record: " + error.message);
  }
}

async function toggleHistoryFavorite(recordId, button) {
  try {
    await apiCall(`/api/history/${recordId}/favorite`, "POST");
    button.classList.toggle("favorited");
    showSuccessMessage(
      button.classList.contains("favorited")
        ? "⭐ Added to favorites"
        : "✨ Removed from favorites"
    );
  } catch (error) {
    showError("Failed to update favorite: " + error.message);
  }
}

async function deleteHistoryRecord(recordId) {
  if (!confirm("Are you sure you want to delete this analysis record?")) return;

  try {
    await apiCall(`/api/history/${recordId}`, "DELETE");
    await loadHistory();
    showSuccessMessage("🗑️ Record deleted successfully");
  } catch (error) {
    showError("Failed to delete record: " + error.message);
  }
}

function filterHistory(filter) {
  // Update active filter button
  document.querySelectorAll(".filter-btn").forEach((btn) => {
    btn.classList.remove("active");
  });
  event.target.classList.add("active");

  loadHistory(filter);
}

// ====================================
// TOGGLE FAVORITE (Current Analysis)
// ====================================
async function toggleFavorite() {
  if (!currentRecordId || !authToken) {
    showError("Please login to add favorites");
    return;
  }

  try {
    await apiCall(`/api/history/${currentRecordId}/favorite`, "POST");

    const btn = document.getElementById("favoriteBtn");
    btn.classList.toggle("favorited");

    showSuccessMessage(
      btn.classList.contains("favorited")
        ? "⭐ Added to favorites"
        : "✨ Removed from favorites"
    );
  } catch (error) {
    showError("Failed to update favorite");
  }
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

function formatCategoryName(category) {
  return category.replace(/_/g, " ").replace(/\b\w/g, (l) => l.toUpperCase());
}

function escapeHtml(text) {
  const div = document.createElement("div");
  div.textContent = text;
  return div.innerHTML;
}

function showError(message) {
  const errorDiv = document.getElementById("errorMessage");
  if (!errorDiv) {
    console.error("Error div not found:", message);
    alert("Error: " + message);
    return;
  }

  errorDiv.innerHTML = `<i class="fas fa-exclamation-circle"></i> ${message}`;
  errorDiv.style.display = "block";

  setTimeout(() => {
    errorDiv.style.display = "none";
  }, 5000);
}

function showSuccessMessage(message) {
  const successDiv = document.createElement("div");
  successDiv.style.cssText = `
    position: fixed;
    top: 90px;
    right: 20px;
    background: linear-gradient(135deg, #38ef7d 0%, #11998e 100%);
    color: white;
    padding: 15px 25px;
    border-radius: 10px;
    box-shadow: 0 5px 15px rgba(0,0,0,0.3);
    z-index: 10001;
    font-weight: 500;
    opacity: 0;
    transform: translateY(-20px);
    transition: all 0.3s ease;
  `;
  successDiv.innerHTML = `<i class="fas fa-check-circle"></i> ${message}`;

  document.body.appendChild(successDiv);

  setTimeout(() => {
    successDiv.style.opacity = "1";
    successDiv.style.transform = "translateY(0)";
  }, 100);

  setTimeout(() => {
    successDiv.style.opacity = "0";
    successDiv.style.transform = "translateY(-20px)";
    setTimeout(() => successDiv.remove(), 400);
  }, 3000);
}

// ====================================
// DOWNLOAD REPORT
// ====================================
function downloadReport() {
  const results = document.getElementById("results");
  if (!results || results.style.display === "none") {
    showError("No results to download!");
    return;
  }

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
  document.getElementById("flaggedSection") &&
  document.getElementById("flaggedSection").style.display !== "none"
    ? "FLAGGED CATEGORIES:\n" +
      document.getElementById("flaggedSection").innerText
    : ""
}

${
  document.getElementById("sentimentSection") &&
  document.getElementById("sentimentSection").style.display !== "none"
    ? "SENTIMENT ANALYSIS:\n" +
      document.getElementById("sentimentSection").innerText
    : ""
}

═══════════════════════════════════════════════════════════════
Report generated by Toxicity Detection System
═══════════════════════════════════════════════════════════════
  `;

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
if (textInput) {
  textInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      analyzeText();
    }
  });
}

document.addEventListener("keydown", (e) => {
  if ((e.ctrlKey || e.metaKey) && e.key === "Enter") {
    e.preventDefault();
    analyzeText();
  }

  // ESC to close modals
  if (e.key === "Escape") {
    closeLoginModal();
    closeRegisterModal();
  }
});

// ====================================
// FILE UPLOAD HANDLING
// ====================================
function initializeFileUpload() {
  const dropzone = document.getElementById("dropzone");
  const fileInput = document.getElementById("fileInput");

  if (!dropzone || !fileInput) return;

  // Click to browse
  dropzone.addEventListener("click", () => fileInput.click());

  // Drag and drop
  dropzone.addEventListener("dragover", (e) => {
    e.preventDefault();
    dropzone.style.borderColor = "var(--gold)";
    dropzone.style.background = "rgba(212, 165, 116, 0.05)";
  });

  dropzone.addEventListener("dragleave", () => {
    dropzone.style.borderColor = "var(--border)";
    dropzone.style.background = "";
  });

  dropzone.addEventListener("drop", (e) => {
    e.preventDefault();
    dropzone.style.borderColor = "var(--border)";
    dropzone.style.background = "";

    const files = e.dataTransfer.files;
    if (files.length > 0) {
      fileInput.files = files;
      handleFileSelect(files[0]);
    }
  });

  fileInput.addEventListener("change", (e) => {
    if (e.target.files.length > 0) {
      handleFileSelect(e.target.files[0]);
    }
  });
}

function handleFileSelect(file) {
  const selectedFileName = document.getElementById("selectedFileName");
  const selectedFileSize = document.getElementById("selectedFileSize");
  const fileSelected = document.getElementById("fileSelected");
  const dropzoneContent = document.querySelector(".dropzone-content");
  const uploadBtn = document.getElementById("uploadBtn");

  if (selectedFileName) selectedFileName.textContent = file.name;
  if (selectedFileSize)
    selectedFileSize.textContent = (file.size / 1024).toFixed(2) + " KB";
  if (fileSelected) fileSelected.style.display = "flex";
  if (dropzoneContent) dropzoneContent.style.display = "none";
  if (uploadBtn) uploadBtn.disabled = false;
}

function removeFile() {
  const fileInput = document.getElementById("fileInput");
  const fileSelected = document.getElementById("fileSelected");
  const dropzoneContent = document.querySelector(".dropzone-content");
  const uploadBtn = document.getElementById("uploadBtn");

  if (fileInput) fileInput.value = "";
  if (fileSelected) fileSelected.style.display = "none";
  if (dropzoneContent) dropzoneContent.style.display = "block";
  if (uploadBtn) uploadBtn.disabled = true;
}

async function uploadFile() {
  const fileInput = document.getElementById("fileInput");
  if (!fileInput || !fileInput.files[0]) return;

  const uploadProgress = document.getElementById("uploadProgress");
  const fileResults = document.getElementById("fileResults");
  const uploadBtn = document.getElementById("uploadBtn");

  if (uploadProgress) uploadProgress.style.display = "block";
  if (fileResults) fileResults.style.display = "none";
  if (uploadBtn) uploadBtn.disabled = true;

  const formData = new FormData();
  formData.append("file", fileInput.files[0]);

  try {
    const response = await fetch("/api/upload", {
      method: "POST",
      body: formData,
      headers: authToken ? { Authorization: `Bearer ${authToken}` } : {},
    });

    const data = await response.json();

    if (response.ok) {
      displayFileResults(data);
    } else {
      showError(data.error || "Upload failed");
    }
  } catch (error) {
    showError("Error uploading file: " + error.message);
  } finally {
    if (uploadProgress) uploadProgress.style.display = "none";
    if (uploadBtn) uploadBtn.disabled = false;
  }
}

function displayFileResults(data) {
  const resultsDiv = document.getElementById("fileResults");
  const statsDiv = document.getElementById("fileStats");
  const tableDiv = document.getElementById("resultsTable");

  if (!resultsDiv || !statsDiv || !tableDiv) return;

  const toxicPercent = ((data.toxic_count / data.analyzed_lines) * 100).toFixed(
    1
  );

  statsDiv.innerHTML = `
    <div class="stat-card">
      <strong>File:</strong> ${escapeHtml(data.filename)}<br>
      <strong>Total Lines:</strong> ${data.analyzed_lines}<br>
      <strong>Toxic:</strong> ${data.toxic_count} (${toxicPercent}%)<br>
      <strong>Safe:</strong> ${data.analyzed_lines - data.toxic_count}
    </div>
  `;

  let tableHTML = `
    <table class="results-table">
      <thead>
        <tr>
          <th>#</th>
          <th>Text Preview</th>
          <th>Score</th>
          <th>Status</th>
        </tr>
      </thead>
      <tbody>
  `;

  data.results.forEach((result) => {
    const statusClass = result.is_toxic ? "status-toxic" : "status-safe";
    const statusText = result.is_toxic ? "⚠️ Toxic" : "✅ Safe";

    tableHTML += `
      <tr>
        <td>${result.line_number}</td>
        <td class="text-preview">${escapeHtml(result.text)}</td>
        <td>${result.toxicity_score}</td>
        <td class="${statusClass}">${statusText}</td>
      </tr>
    `;
  });

  tableHTML += "</tbody></table>";
  tableDiv.innerHTML = tableHTML;

  resultsDiv.style.display = "block";
  resultsDiv.scrollIntoView({ behavior: "smooth", block: "start" });
}

function exportResults() {
  showSuccessMessage("Export feature coming soon!");
}

// ====================================
// INITIALIZATION COMPLETE
// ====================================
console.log("✅ Toxicity Detection System v2.1 loaded successfully!");
console.log("🔧 Token management fixed - history will now save!");
