/* =============================================================
   Study with A.I. — Frontend Logic
   =============================================================
   Responsibilities:
     1. Pill-tab switching between Debugger / Summarizer panels
     2. Loading sample code snippets into the debugger
     3. AJAX (fetch) calls to /api/debug and /api/summarize
     4. Rendering AI results into the terminal / summary box
     5. Interactive MCQ quiz rendering + instant scoring

   No page reloads happen anywhere in this file — every action
   uses fetch() and updates the DOM directly, which is what makes
   this a true single-page AJAX experience.
   ============================================================= */

document.addEventListener("DOMContentLoaded", () => {
  initTabs();
  loadSampleSnippets();
  bindDebugger();
  bindSummarizer();
  bindQuizSubmit();
});

/* ---------------------------------------------------------------
   1. PILL-TAB SWITCHING
   --------------------------------------------------------------- */
function initTabs() {
  const tabs = document.querySelectorAll(".pill-tab");

  tabs.forEach((tab) => {
    tab.addEventListener("click", () => {
      tabs.forEach((t) => t.classList.remove("active"));
      tab.classList.add("active");

      document.querySelectorAll(".tool-panel").forEach((panel) => {
        panel.classList.toggle("active", panel.id === tab.dataset.target);
      });
    });
  });
}

/* ---------------------------------------------------------------
   2. SAMPLE CODE PLAYGROUND — populate + wire the dropdown
   --------------------------------------------------------------- */
async function loadSampleSnippets() {
  try {
    const res = await fetch("/api/samples");
    const json = await res.json();
    if (!json.success) return;

    const select = document.getElementById("sampleSelect");

    json.data.forEach((snippet) => {
      const opt = document.createElement("option");
      opt.value = snippet.id;
      opt.textContent = snippet.name;
      opt.dataset.language = snippet.language;
      opt.dataset.code = snippet.code;
      select.appendChild(opt);
    });

    select.addEventListener("change", () => {
      const chosen = select.options[select.selectedIndex];
      if (!chosen.value) return;

      document.getElementById("codeInput").value = chosen.dataset.code;

      const langSelect = document.getElementById("languageSelect");
      langSelect.value = chosen.dataset.language;
      updateLangBadge(chosen.dataset.language);
    });
  } catch (err) {
    console.error("Failed to load sample snippets:", err);
  }
}

function updateLangBadge(lang) {
  document.getElementById("langBadge").textContent = lang.toUpperCase();
}

/* ---------------------------------------------------------------
   3. FEATURE 1 — AI CODE DEBUGGER
   --------------------------------------------------------------- */
function bindDebugger() {
  const languageSelect = document.getElementById("languageSelect");
  languageSelect.addEventListener("change", () => updateLangBadge(languageSelect.value));

  document.getElementById("debugBtn").addEventListener("click", async () => {
    const code = document.getElementById("codeInput").value.trim();
    const language = languageSelect.value;

    const terminal = document.getElementById("debugTerminal");
    const statusBadge = document.getElementById("debugStatusBadge");
    const btn = document.getElementById("debugBtn");

    if (!code) {
      terminal.innerHTML = `<p class="bug-item">Please paste some code or select a sample first.</p>`;
      return;
    }

    setLoading(btn, true, "Analyzing...");
    setBadge(statusBadge, "RUNNING", "badge-lang");
    terminal.innerHTML = `<p class="terminal-hint">$ Sending code to AI model...</p>`;

    try {
      const res = await fetch("/api/debug", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ code, language }),
      });
      const json = await res.json();

      if (!json.success) throw new Error(json.error || "Unknown error occurred.");

      renderDebugResult(json.data, terminal);
      setBadge(
        statusBadge,
        json.data.has_bugs ? "BUGS FOUND" : "CLEAN",
        json.data.has_bugs ? "badge-error" : "badge-success"
      );
    } catch (err) {
      terminal.innerHTML = `<p class="bug-item">Error: ${escapeHtml(err.message)}</p>`;
      setBadge(statusBadge, "ERROR", "badge-error");
    } finally {
      setLoading(btn, false, '<span class="btn-icon">⚡</span> Debug My Code');
    }
  });
}

function renderDebugResult(data, terminal) {
  let html = "";

  html += `<div class="terminal-section-title">Bugs Detected</div>`;
  if (data.bugs && data.bugs.length > 0) {
    data.bugs.forEach((bug) => {
      const linePrefix = bug.line ? `Line ${bug.line}: ` : "";
      html += `<p class="bug-item">${linePrefix}${escapeHtml(bug.issue)}</p>`;
    });
  } else {
    html += `<p style="color: var(--success-green);">✓ No bugs detected.</p>`;
  }

  html += `<div class="terminal-section-title">Explanation</div>`;
  html += `<p>${escapeHtml(data.explanation)}</p>`;

  html += `<div class="terminal-section-title">Corrected Code</div>`;
  html += `<pre>${escapeHtml(data.corrected_code)}</pre>`;

  terminal.innerHTML = html;
}

/* ---------------------------------------------------------------
   4. FEATURE 2 — TOPIC SUMMARIZER + MCQ GENERATOR
   --------------------------------------------------------------- */
function bindSummarizer() {
  document.getElementById("summarizeBtn").addEventListener("click", async () => {
    const text = document.getElementById("notesInput").value.trim();

    const summaryBox = document.getElementById("summaryBox");
    const statusBadge = document.getElementById("summaryStatusBadge");
    const btn = document.getElementById("summarizeBtn");
    const quizCard = document.getElementById("quizCard");

    if (!text) {
      summaryBox.innerHTML = `<p class="bug-item">Please paste some study notes first.</p>`;
      return;
    }

    setLoading(btn, true, "Generating...");
    setBadge(statusBadge, "RUNNING", "badge-lang");
    summaryBox.innerHTML = `<p class="terminal-hint">Generating summary and quiz...</p>`;
    quizCard.style.display = "none";

    try {
      const res = await fetch("/api/summarize", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text }),
      });
      const json = await res.json();

      if (!json.success) throw new Error(json.error || "Unknown error occurred.");

      summaryBox.textContent = json.data.summary;
      setBadge(statusBadge, "DONE", "badge-success");

      renderQuiz(json.data.mcqs || []);
      quizCard.style.display = "block";
    } catch (err) {
      summaryBox.innerHTML = `<p class="bug-item">Error: ${escapeHtml(err.message)}</p>`;
      setBadge(statusBadge, "ERROR", "badge-error");
    } finally {
      setLoading(btn, false, '<span class="btn-icon">✨</span> Summarize & Generate Quiz');
    }
  });
}

/* Keeps the current quiz's correct answers in memory for instant checking */
let currentQuiz = [];

function renderQuiz(mcqs) {
  currentQuiz = mcqs;
  const container = document.getElementById("quizContainer");
  container.innerHTML = "";

  mcqs.forEach((q, qIndex) => {
    const qDiv = document.createElement("div");
    qDiv.className = "quiz-question";
    qDiv.dataset.qIndex = qIndex;

    let optionsHtml = "";
    (q.options || []).forEach((opt, oIndex) => {
      optionsHtml += `
        <div class="quiz-option" data-option-index="${oIndex}">
          <span>${String.fromCharCode(65 + oIndex)}.</span> <span>${escapeHtml(opt)}</span>
        </div>`;
    });

    qDiv.innerHTML = `
      <div class="quiz-question-title">Q${qIndex + 1}. ${escapeHtml(q.question)}</div>
      ${optionsHtml}
    `;
    container.appendChild(qDiv);
  });

  // Let the user click an option to select it (before checking answers)
  container.querySelectorAll(".quiz-question").forEach((qDiv) => {
    qDiv.querySelectorAll(".quiz-option").forEach((optDiv) => {
      optDiv.addEventListener("click", () => {
        qDiv.querySelectorAll(".quiz-option").forEach((o) => o.classList.remove("selected"));
        optDiv.classList.add("selected");
      });
    });
  });

  document.getElementById("quizScoreBadge").textContent = `0 / ${mcqs.length}`;
}

function bindQuizSubmit() {
  document.getElementById("submitQuizBtn").addEventListener("click", checkQuizAnswers);
}

function checkQuizAnswers() {
  let score = 0;
  const questionDivs = document.querySelectorAll(".quiz-question");

  questionDivs.forEach((qDiv, qIndex) => {
    const correctIndex = currentQuiz[qIndex].correct_index;
    const selected = qDiv.querySelector(".quiz-option.selected");
    const options = qDiv.querySelectorAll(".quiz-option");

    // Always reveal the correct option in green
    options.forEach((opt, oIndex) => {
      opt.classList.remove("correct", "incorrect");
      if (oIndex === correctIndex) opt.classList.add("correct");
    });

    if (selected) {
      const selectedIndex = parseInt(selected.dataset.optionIndex, 10);
      if (selectedIndex === correctIndex) {
        score++;
      } else {
        selected.classList.add("incorrect");
      }
    }
  });

  document.getElementById("quizScoreBadge").textContent = `${score} / ${questionDivs.length}`;
}

/* ---------------------------------------------------------------
   5. SMALL UTILITIES
   --------------------------------------------------------------- */
function setLoading(btn, isLoading, label) {
  btn.disabled = isLoading;
  btn.innerHTML = label;
}

function setBadge(badgeEl, text, className) {
  badgeEl.textContent = text;
  badgeEl.className = `badge ${className}`;
}

/* Prevents AI-returned text/code from breaking the page or enabling XSS */
function escapeHtml(str) {
  const div = document.createElement("div");
  div.textContent = str == null ? "" : String(str);
  return div.innerHTML;
}
