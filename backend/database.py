"""
Database module for SRM AI Admission Chatbot.
Handles SQLite database connection, table initialization, saving chat logs,
and retrieving conversation history.
"""

import os
import json
import sqlite3
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone


def get_db_path(custom_path: Optional[str] = None) -> str:
    """Returns the effective database file path."""
    return custom_path or os.getenv("DATABASE_PATH", "chatbot.db")


def get_db_connection(db_path: Optional[str] = None) -> sqlite3.Connection:
    """
    Establishes and returns a connection to the SQLite database.
    Configures row_factory to return dict-like sqlite3.Row objects.
    """
    path = get_db_path(db_path)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_path: Optional[str] = None) -> None:
    """
    Initializes the SQLite database schema if it doesn't already exist.
    Creates the 'chat_logs' table to store user interactions and predictions.
    """
    path = get_db_path(db_path)
    with get_db_connection(path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS chat_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                user_message TEXT NOT NULL,
                intent TEXT NOT NULL,
                confidence REAL NOT NULL,
                bot_response TEXT NOT NULL,
                entities TEXT DEFAULT '[]',
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_session_id ON chat_logs(session_id)
            """
        )
        conn.commit()


def save_chat_log(
    session_id: str,
    user_message: str,
    intent: str,
    confidence: float,
    bot_response: str,
    entities: Optional[List[Dict[str, Any]]] = None,
    db_path: Optional[str] = None
) -> Dict[str, Any]:
    """
    Persists a chat interaction record into the SQLite database.

    Args:
        session_id: Unique identifier for the user session.
        user_message: The original prompt sent by the user.
        intent: The predicted intent category.
        confidence: Prediction confidence score (0.0 to 1.0).
        bot_response: Dynamic answer returned by the chatbot.
        entities: List of extracted named entities.
        db_path: Optional custom path to SQLite database.

    Returns:
        Dict representing the newly inserted chat log record.
    """
    # Auto-initialize table if database has not been initialized yet
    init_db(db_path)

    path = get_db_path(db_path)
    entities_json = json.dumps(entities if entities is not None else [])
    current_ts = datetime.now(timezone.utc).isoformat()

    with get_db_connection(path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO chat_logs (session_id, user_message, intent, confidence, bot_response, entities, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (session_id, user_message, intent, float(confidence), bot_response, entities_json, current_ts)
        )
        log_id = cursor.lastrowid
        conn.commit()

    return {
        "id": log_id,
        "session_id": session_id,
        "user_message": user_message,
        "intent": intent,
        "confidence": confidence,
        "bot_response": bot_response,
        "entities": entities or [],
        "timestamp": current_ts
    }


def get_chat_history(session_id: str, db_path: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Retrieves all conversation logs for a given session_id in chronological order.

    Args:
        session_id: Unique session identifier.
        db_path: Optional custom path to SQLite database.

    Returns:
        List of dictionaries containing conversation records.
    """
    init_db(db_path)

    path = get_db_path(db_path)
    with get_db_connection(path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT id, session_id, user_message, intent, confidence, bot_response, entities, timestamp
            FROM chat_logs
            WHERE session_id = ?
            ORDER BY id ASC
            """,
            (session_id,)
        )
        rows = cursor.fetchall()

    history = []
    for row in rows:
        entities_data = []
        if row["entities"]:
            try:
                entities_data = json.loads(row["entities"])
            except Exception:
                entities_data = []

        history.append({
            "id": row["id"],
            "session_id": row["session_id"],
            "user_message": row["user_message"],
            "intent": row["intent"],
            "confidence": round(row["confidence"], 4),
            "bot_response": row["bot_response"],
            "entities": entities_data,
            "timestamp": row["timestamp"]
        })

    return history
