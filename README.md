# Study with A.I. 🧠⚡

An AI-assisted study companion built with a **Python (Flask) backend** and a
vanilla **HTML/CSS/JS** frontend, styled in a dark "cyberpunk developer"
theme. Built as a B.Sc. IT college project.

## Features

1. **AI Code Debugger** — paste Python / Java / C / JavaScript code (or load
   a pre-loaded buggy sample), and the AI detects bugs, explains why the
   code fails, and returns a corrected version.
2. **AI Topic Summarizer + MCQ Generator** — paste study notes and get a
   concise summary plus a 5-question multiple-choice quiz with instant
   scoring.
3. **Sample Code Playground** — pre-loaded snippets with intentional bugs
   across 4 languages, so you can test the debugger immediately.

## Tech Stack

| Layer      | Technology                                   |
|------------|-----------------------------------------------|
| Backend    | Python 3, Flask                               |
| AI         | Google Gemini (default) or OpenAI GPT         |
| Frontend   | HTML5, CSS3 (CSS variables), vanilla JS (fetch/AJAX) |
| Fonts      | 'Fira Code' (code), 'Inter' (UI text)         |

## Folder Structure

```
study-with-ai/
├── app.py                # Flask routes (HTTP layer only)
├── ai_service.py         # All AI/API logic (Gemini + OpenAI)
├── sample_code.py        # Pre-loaded buggy code snippets
├── requirements.txt      # Python dependencies
├── .env.example          # Template for your API keys
├── .gitignore
├── templates/
│   └── index.html        # Single-page app shell (2-column layout)
└── static/
    ├── css/
    │   └── style.css     # Cyberpunk theme (CSS variables, glow effects)
    └── js/
        └── main.js       # Tab switching, fetch() calls, MCQ logic
```

### Why this structure? (for your viva/examiners)

- **`app.py`** only handles HTTP request/response plumbing — it never talks
  to the AI API directly.
- **`ai_service.py`** is the single place that builds prompts, calls
  Gemini/OpenAI, and parses the JSON response. If you ever want to switch
  providers or add a new one, you only touch this file.
- **`sample_code.py`** holds static reference data, kept separate from
  route logic.
- This is the standard Flask "separation of concerns" pattern: **routes →
  services → data**.

## Setup Guide

### 1. Create and activate a virtual environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure your API key

Copy the example env file:

```bash
# Windows
copy .env.example .env

# macOS / Linux
cp .env.example .env
```

Open `.env` and paste in your real API key:

```env
AI_PROVIDER=gemini
GEMINI_API_KEY=your-actual-gemini-key
```

> Get a **free** Gemini API key at https://aistudio.google.com/app/apikey
> (Google's Gemini has a generous free tier, ideal for a college project).
> If you'd rather use OpenAI, set `AI_PROVIDER=openai` and fill in
> `OPENAI_API_KEY` instead — `ai_service.py` already supports both.

### 4. Run the Flask server

```bash
python app.py
```

Then open your browser at **http://127.0.0.1:5000**

### 5. (Optional) Verify everything is wired up

Visit **http://127.0.0.1:5000/api/health** — you should see:

```json
{"status": "ok", "ai_provider": "gemini"}
```

## How It Works (Architecture Overview)

```
 Browser (index.html + main.js)
        │  fetch() POST /api/debug or /api/summarize
        ▼
 Flask app.py  ──────────────►  ai_service.py  ──────────►  Gemini / OpenAI API
        │                              │
        │  builds prompt, parses JSON  │
        ◄──────────────────────────────
        │  returns clean JSON
        ▼
 Browser renders result into the
 terminal console / summary box / MCQ quiz
        (NO page reload — pure AJAX)
```

1. The user pastes code or notes and clicks a neon action button.
2. `main.js` sends a `fetch()` POST request to a Flask API route.
3. Flask validates the input and calls the matching function in
   `ai_service.py`.
4. `ai_service.py` sends a carefully engineered prompt to Gemini/OpenAI,
   requesting **strict JSON** back (bugs, explanation, corrected code — or
   summary + 5 MCQs).
5. Flask returns that JSON to the browser as `{"success": true, "data": ...}`.
6. `main.js` renders it into the terminal console, summary box, or an
   interactive quiz — all without reloading the page.

## Troubleshooting

| Problem | Fix |
|---|---|
| `GEMINI_API_KEY is missing` error | Make sure you created `.env` (not just `.env.example`) and pasted a real key |
| Blank quiz / summary | Check your terminal running `python app.py` for the full error traceback |
| `ModuleNotFoundError` | Re-run `pip install -r requirements.txt` inside your activated venv |
