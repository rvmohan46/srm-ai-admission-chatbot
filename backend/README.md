---
title: SRM AI Admission Chatbot Backend
emoji: 🎓
colorFrom: blue
colorTo: indigo
sdk: docker
app_port: 7860
pinned: false
---

# SRM AI Admission Chatbot - Flask NLP Backend

Flask REST API backend for the SRM AI Admission Chatbot. Powered by NLTK, spaCy NER, and Hugging Face `facebook/bart-large-mnli` zero-shot intent classification.

## API Endpoints

- `GET /api/v1/health` — Health check
- `POST /api/chat` — Process admission query
- `GET /api/v1/history/<session_id>` — Chat history
