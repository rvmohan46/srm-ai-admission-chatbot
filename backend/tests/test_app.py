"""
Automated Unit and Integration Tests for SRM AI Admission Chatbot.
Tests database, NLP engine, Flask REST API endpoints, and error validation.
"""

import os
import json
import tempfile
import unittest
from unittest.mock import patch, MagicMock

import sys

# Ensure backend directory is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Set test environment
os.environ["DATABASE_PATH"] = ":memory:"

from app import app
from database import init_db, save_chat_log, get_chat_history
from nlp_engine import NLPEngine, INTENTS


class TestDatabaseOperations(unittest.TestCase):
    def setUp(self):
        self.db_fd, self.db_path = tempfile.mkstemp()
        init_db(self.db_path)

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(self.db_path)

    def test_save_and_retrieve_chat_history(self):
        session_id = "test_session_101"
        log = save_chat_log(
            session_id=session_id,
            user_message="What is the tuition fee for B.Tech CSE?",
            intent="fee_structure",
            confidence=0.95,
            bot_response="The B.Tech fee ranges from ₹2,50,000 to ₹4,50,000.",
            entities=[{"text": "B.Tech CSE", "label": "DEGREE_PROGRAM"}],
            db_path=self.db_path
        )
        self.assertIsNotNone(log.get("id"))
        self.assertEqual(log["session_id"], session_id)

        history = get_chat_history(session_id, db_path=self.db_path)
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0]["intent"], "fee_structure")
        self.assertEqual(history[0]["user_message"], "What is the tuition fee for B.Tech CSE?")
        self.assertEqual(len(history[0]["entities"]), 1)


class TestNLPEngine(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.nlp = NLPEngine()

    def test_preprocess_text(self):
        raw_text = "What ARE the requirements for B.Tech Admissions in 2026???"
        processed = self.nlp.preprocess_text(raw_text)
        self.assertIn("requirement", processed)

    def test_extract_entities(self):
        text = "I want to apply for B.Tech at Kattankulathur campus via SRMJEEE."
        entities = self.nlp.extract_entities(text)
        labels = [e["label"] for e in entities]
        self.assertTrue("DEGREE_PROGRAM" in labels or "CAMPUS_LOCATION" in labels or "ENTRANCE_EXAM" in labels)

    def test_keyword_fallback_intent(self):
        intent, conf = self.nlp._keyword_fallback_intent("Where are the campus locations?")
        self.assertEqual(intent, "campus_locations")
        self.assertGreaterEqual(conf, 0.5)

    def test_generate_response(self):
        response = self.nlp.generate_response("scholarships", [])
        self.assertIn("Scholarship", response)


class TestFlaskAPI(unittest.TestCase):
    def setUp(self):
        self.db_fd, self.db_path = tempfile.mkstemp()
        os.environ["DATABASE_PATH"] = self.db_path
        init_db(self.db_path)
        app.config["TESTING"] = True
        self.client = app.test_client()

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(self.db_path)

    def test_health_endpoint(self):
        response = self.client.get("/api/v1/health")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data["status"], "OK")
        self.assertIn("timestamp", data)

    def test_chat_endpoint_missing_payload(self):
        response = self.client.post("/api/v1/chat", data="not json", content_type="text/plain")
        self.assertEqual(response.status_code, 400)

    def test_chat_endpoint_missing_session_id(self):
        response = self.client.post(
            "/api/v1/chat",
            data=json.dumps({"message": "Hello"}),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 400)
        data = response.get_json()
        self.assertIn("session_id", data["message"])

    def test_chat_endpoint_missing_message(self):
        response = self.client.post(
            "/api/v1/chat",
            data=json.dumps({"session_id": "sess_1"}),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 400)
        data = response.get_json()
        self.assertIn("message", data["message"])

    @patch.object(NLPEngine, "classify_intent", return_value=("general_greeting", 0.98))
    def test_chat_endpoint_success(self, mock_classify):
        payload = {
            "session_id": "test_sess_001",
            "message": "Hello, I want to know about SRM admissions!"
        }
        response = self.client.post(
            "/api/v1/chat",
            data=json.dumps(payload),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data["session_id"], "test_sess_001")
        self.assertEqual(data["intent"], "general_greeting")
        self.assertIn("bot_response", data)
        self.assertIn("timestamp", data)

        # Test History retrieval for session
        hist_response = self.client.get(f"/api/v1/history/{payload['session_id']}")
        self.assertEqual(hist_response.status_code, 200)
        hist_data = hist_response.get_json()
        self.assertEqual(hist_data["count"], 1)
        self.assertEqual(hist_data["history"][0]["session_id"], "test_sess_001")


if __name__ == "__main__":
    unittest.main()
