"""
ai_service.py
==============
This module is the ONLY file that talks to an external AI API.

Keeping all AI logic in one place makes the project modular and easy
to explain in a viva/exam: if you ever want to switch from Gemini to
OpenAI (or add another provider), you only change code here — app.py
and the frontend never need to know or care which provider is used.

Supported providers (set AI_PROVIDER in your .env file):
    - "gemini"  -> uses Google Generative AI (Gemini)
    - "openai"  -> uses OpenAI's Chat Completions API

Both providers are instructed to return STRICT JSON, so the Flask
backend can parse it reliably and hand clean, predictable data to the
frontend JavaScript.
"""

import os
import json
import re

# Read once at import time. Changing .env requires restarting the server,
# which is expected Flask behaviour for environment variables.
AI_PROVIDER = os.getenv("AI_PROVIDER", "gemini").lower()


class AIServiceError(Exception):
    """
    Raised whenever the AI API call fails, times out, is missing an
    API key, or returns something we cannot parse as JSON.

    app.py catches this specific exception to return a clean, friendly
    error message (HTTP 502) instead of a generic server crash (500).
    """
    pass


# ---------------------------------------------------------------------------
# LOW-LEVEL CALL: routes the prompt to whichever provider is configured
# ---------------------------------------------------------------------------
def _call_ai(prompt: str) -> str:
    """Sends `prompt` to the configured AI provider and returns raw text."""
    if AI_PROVIDER == "gemini":
        return _call_gemini(prompt)
    elif AI_PROVIDER == "openai":
        return _call_openai(prompt)
    else:
        raise AIServiceError(
            f"Unknown AI_PROVIDER '{AI_PROVIDER}' in .env. Use 'gemini' or 'openai'."
        )


def _call_gemini(prompt: str) -> str:
    try:
        import google.generativeai as genai
    except ImportError:
        raise AIServiceError(
            "google-generativeai is not installed. Run: pip install -r requirements.txt"
        )

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key or api_key == "your-gemini-api-key-here":
        raise AIServiceError(
            "GEMINI_API_KEY is missing. Add your key to the .env file (see .env.example)."
        )

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(
        model_name="gemini-3.6-flash",
        # Ask Gemini natively for JSON output — avoids markdown fences.
        generation_config={"response_mime_type": "application/json"},
    )
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        raise AIServiceError(f"Gemini API call failed: {str(e)}")


def _call_openai(prompt: str) -> str:
    try:
        from openai import OpenAI
    except ImportError:
        raise AIServiceError(
            "openai package is not installed. Run: pip install -r requirements.txt"
        )

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key or api_key == "your-openai-api-key-here":
        raise AIServiceError(
            "OPENAI_API_KEY is missing. Add your key to the .env file (see .env.example)."
        )

    client = OpenAI(api_key=api_key)
    try:
        response = client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
        )
        return response.choices[0].message.content
    except Exception as e:
        raise AIServiceError(f"OpenAI API call failed: {str(e)}")


# ---------------------------------------------------------------------------
# HELPER: safely parse JSON even if the model wraps it in ```json fences
# ---------------------------------------------------------------------------
def _parse_json(raw_text: str) -> dict:
    cleaned = re.sub(r"^```json|```$", "", raw_text.strip(), flags=re.MULTILINE).strip()
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        raise AIServiceError("The AI returned an unexpected format. Please try again.")


# ---------------------------------------------------------------------------
# FEATURE 1: AI CODE DEBUGGER
# ---------------------------------------------------------------------------
def debug_code(code: str, language: str) -> dict:
    """
    Sends source code to the AI and asks it to:
      1. Detect bugs
      2. Explain why the code fails
      3. Provide a corrected version

    Returns a dict matching this shape:
        {
          "has_bugs": bool,
          "bugs": [{"line": int|None, "issue": str}, ...],
          "explanation": str,
          "corrected_code": str
        }
    """
    prompt = f"""
You are an expert {language} code reviewer helping a college student.
Analyze the following {language} code and respond with STRICT JSON ONLY
(no markdown, no commentary outside the JSON) using this exact schema:

{{
  "has_bugs": true or false,
  "bugs": [
    {{"line": <int or null>, "issue": "<short description of the bug>"}}
  ],
  "explanation": "<clear, beginner-friendly explanation of WHY it fails>",
  "corrected_code": "<the full corrected code as a single string>"
}}

If the code has no bugs, set "has_bugs" to false, leave "bugs" as an empty
list, briefly explain why it is correct, and return the code unchanged in
"corrected_code".

CODE TO ANALYZE:
---
{code}
---
"""
    raw = _call_ai(prompt)
    data = _parse_json(raw)

    # Safety-net defaults so a slightly malformed AI response never
    # crashes the frontend rendering logic.
    data.setdefault("has_bugs", False)
    data.setdefault("bugs", [])
    data.setdefault("explanation", "No explanation returned.")
    data.setdefault("corrected_code", code)
    return data


# ---------------------------------------------------------------------------
# FEATURE 2: TOPIC SUMMARIZER + MCQ GENERATOR
# ---------------------------------------------------------------------------
def summarize_and_generate_mcqs(text: str) -> dict:
    """
    Sends study notes to the AI and asks it to:
      1. Write a concise summary
      2. Generate exactly 5 multiple-choice questions based on the notes

    Returns a dict matching this shape:
        {
          "summary": str,
          "mcqs": [
            {
              "question": str,
              "options": [str, str, str, str],
              "correct_index": int,   # 0-based
              "explanation": str
            },
            ... x5
          ]
        }
    """
    prompt = f"""
You are an expert study assistant helping a college student revise.
Read the study notes below and respond with STRICT JSON ONLY
(no markdown, no commentary outside the JSON) using this exact schema:

{{
  "summary": "<concise 3-5 sentence summary of the notes>",
  "mcqs": [
    {{
      "question": "<question text>",
      "options": ["<option A>", "<option B>", "<option C>", "<option D>"],
      "correct_index": <0-3>,
      "explanation": "<why this answer is correct, 1 sentence>"
    }}
    ... exactly 5 questions total ...
  ]
}}

Rules:
- Generate EXACTLY 5 multiple choice questions.
- Each question must have exactly 4 options.
- "correct_index" is zero-based (0 = first option, 3 = last option).
- Base every question strictly on the notes provided below.

STUDY NOTES:
---
{text}
---
"""
    raw = _call_ai(prompt)
    data = _parse_json(raw)

    data.setdefault("summary", "No summary returned.")
    data.setdefault("mcqs", [])
    return data
