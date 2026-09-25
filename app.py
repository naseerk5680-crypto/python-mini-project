
import os
import traceback

from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv

import ai_service
from sample_code import SAMPLE_SNIPPETS

load_dotenv()  # reads key=value pairs from .env into os.environ

app = Flask(__name__)
app.config["JSON_SORT_KEYS"] = False  # keep our JSON key order as written


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/api/debug", methods=["POST"])
def debug_code():
    try:
        payload = request.get_json(force=True) or {}
        code = (payload.get("code") or "").strip()
        language = (payload.get("language") or "python").strip().lower()

        if not code:
            return jsonify({
                "success": False,
                "error": "No code provided. Please paste or select a snippet."
            }), 400

        result = ai_service.debug_code(code, language)
        return jsonify({"success": True, "data": result})

    except ai_service.AIServiceError as e:
        # A known, expected failure (bad/missing API key, AI returned junk, etc.)
        return jsonify({"success": False, "error": str(e)}), 502

    except Exception as e:
        # An unexpected failure — log the full traceback to the server
        # console for debugging, but keep the client-facing message clean.
        traceback.print_exc()
        return jsonify({"success": False, "error": f"Server error: {str(e)}"}), 500


@app.route("/api/summarize", methods=["POST"])
def summarize_topic():
    try:
        payload = request.get_json(force=True) or {}
        text = (payload.get("text") or "").strip()

        if not text or len(text) < 30:
            return jsonify({
                "success": False,
                "error": "Please paste at least a short paragraph (30+ characters) of study notes."
            }), 400

        result = ai_service.summarize_and_generate_mcqs(text)
        return jsonify({"success": True, "data": result})

    except ai_service.AIServiceError as e:
        return jsonify({"success": False, "error": str(e)}), 502

    except Exception as e:
        traceback.print_exc()
        return jsonify({"success": False, "error": f"Server error: {str(e)}"}), 500


@app.route("/api/samples")
def get_samples():
    return jsonify({"success": True, "data": SAMPLE_SNIPPETS})


@app.route("/api/health")
def health():
    return jsonify({
        "status": "ok",
        "ai_provider": os.getenv("AI_PROVIDER", "gemini"),
    })


if __name__ == "__main__":
    debug_mode = os.getenv("FLASK_DEBUG", "True") == "True"
    app.run(debug=debug_mode, host="0.0.0.0", port=5000)
