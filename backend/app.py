"""
Flask REST API for SRM AI Admission Chatbot.
Provides endpoints for health check, chat execution, and chat history retrieval.
"""

import os
import logging
from datetime import datetime, timezone
from typing import Tuple, List, Dict, Any
from flask import Flask, request, jsonify, Response, render_template
from flask_cors import CORS

from database import init_db, save_chat_log, get_chat_history
from nlp_engine import NLPEngine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "frontend"))

# Initialize Flask App pointing to frontend templates and static assets
app = Flask(
    __name__,
    template_folder=os.path.join(FRONTEND_DIR, "templates"),
    static_folder=os.path.join(FRONTEND_DIR, "static")
)
CORS(app, resources={r"/*": {"origins": "*"}})

# Initialize Database Schema on Application Startup
with app.app_context():
    init_db()

# Lazy Singleton Instance of NLP Engine
_nlp_engine_instance = None

def get_nlp_engine() -> NLPEngine:
    """Returns singleton instance of NLPEngine."""
    global _nlp_engine_instance
    if _nlp_engine_instance is None:
        logger.info("Initializing NLP Engine...")
        _nlp_engine_instance = NLPEngine()
    return _nlp_engine_instance


# -----------------------------------------------------------------------------
# Frontend Route
# -----------------------------------------------------------------------------

@app.route("/", methods=["GET"])
def index():
    """Renders SRM AI Admission Portal Frontend UI."""
    return render_template("index.html")


# -----------------------------------------------------------------------------
# Error Handlers
# -----------------------------------------------------------------------------

@app.errorhandler(400)
def bad_request(error):
    return jsonify({
        "error": "Bad Request",
        "message": getattr(error, "description", str(error))
    }), 400


@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "error": "Not Found",
        "message": getattr(error, "description", "Requested resource was not found.")
    }), 404


@app.errorhandler(500)
def internal_server_error(error):
    logger.error(f"Internal Server Error: {error}")
    return jsonify({
        "error": "Internal Server Error",
        "message": "An unexpected server error occurred."
    }), 500


# -----------------------------------------------------------------------------
# API Endpoints
# -----------------------------------------------------------------------------

@app.route("/api/v1/health", methods=["GET"])
def health_check() -> Tuple[Response, int]:
    """
    GET /api/v1/health
    Returns service health status and timestamp.
    """
    return jsonify({
        "status": "OK",
        "service": "SRM AI Admission Chatbot API",
        "version": "1.0.0",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }), 200


@app.route("/api/v1/chat", methods=["POST"])
@app.route("/api/chat", methods=["POST"])
def chat():
    """
    POST /api/v1/chat or /api/chat
    Payload: {"session_id": "string", "message": "string"}
    
    1. Preprocesses query using NLTK.
    2. Extracts entities using spaCy.
    3. Classifies query into 15+ FAQ intents using Hugging Face Zero-Shot Classifier.
    4. Selects dynamic response.
    5. Saves interaction log to SQLite database.
    """
    if not request.is_json:
        return jsonify({"error": "Bad Request", "message": "Content-Type must be application/json"}), 400

    data = request.get_json()
    if not data or not isinstance(data, dict):
        return jsonify({"error": "Bad Request", "message": "Payload must be a JSON object"}), 400

    message = data.get("message")
    session_id = data.get("session_id") or "session_default"

    if not message or not isinstance(message, str) or not message.strip():
        return jsonify({"error": "Bad Request", "message": "'message' is required and must be a non-empty string."}), 400

    session_id = str(session_id).strip()
    message = message.strip()

    try:
        # Run NLP Pipeline
        nlp = get_nlp_engine()
        nlp_result = nlp.process_query(message)

        # Save to Database
        log_record = save_chat_log(
            session_id=session_id,
            user_message=message,
            intent=nlp_result["intent"],
            confidence=nlp_result["confidence"],
            bot_response=nlp_result["bot_response"],
            entities=nlp_result["entities"]
        )

        response_payload = {
            "session_id": session_id,
            "user_message": message,
            "preprocessed_message": nlp_result["preprocessed_message"],
            "intent": nlp_result["intent"],
            "confidence": nlp_result["confidence"],
            "entities": nlp_result["entities"],
            "bot_response": nlp_result["bot_response"],
            "reply": nlp_result["bot_response"],
            "timestamp": log_record["timestamp"]
        }

        return jsonify(response_payload), 200

    except Exception as e:
        logger.exception("Error processing chat request")
        return jsonify({"error": "Internal Server Error", "message": str(e)}), 500


@app.route("/api/v1/history/<session_id>", methods=["GET"])
def get_history(session_id: str):
    """
    GET /api/v1/history/<session_id>
    Fetches and returns all stored conversation logs for given session_id ordered chronologically.
    """
    if not session_id or not session_id.strip():
        return jsonify({"error": "Bad Request", "message": "'session_id' parameter cannot be empty."}), 400

    try:
        history = get_chat_history(session_id.strip())
        return jsonify({
            "session_id": session_id.strip(),
            "history": history,
            "count": len(history)
        }), 200
    except Exception as e:
        logger.exception(f"Error fetching history for session {session_id}")
        return jsonify({"error": "Internal Server Error", "message": str(e)}), 500


# -----------------------------------------------------------------------------
# Server Entrypoint
# -----------------------------------------------------------------------------

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    host = os.getenv("HOST", "0.0.0.0")
    logger.info(f"Starting SRM AI Admission Chatbot server on {host}:{port}...")
    app.run(host=host, port=port, debug=False)
