# SRM AI Admission Chatbot Backend

A production-ready Python backend repository for the **SRM AI Admission Chatbot**. Built with Flask REST API, SQLite storage, an intelligent NLP pipeline (NLTK, spaCy NER, Hugging Face Zero-Shot Intent Classification), and Docker containerization.

---

## Architecture Overview

```
                          ┌────────────────────────┐
                          │    Client / Frontend   │
                          └───────────┬────────────┘
                                      │ HTTP REST
                                      ▼
                          ┌────────────────────────┐
                          │    Flask API Server    │
                          │        (app.py)        │
                          └─────┬────────────┬─────┘
                                │            │
                      Process   │            │ DB Persist
                      Query     ▼            ▼
            ┌──────────────────────┐    ┌──────────────────────┐
            │      NLP Engine      │    │    SQLite Database   │
            │   (nlp_engine.py)    │    │    (database.py)     │
            ├──────────────────────┤    └──────────────────────┘
            │ 1. NLTK Preprocess   │
            │ 2. spaCy NER         │
            │ 3. HF Zero-Shot      │
            │    (bart-large-mnli) │
            │ 4. FAQ Generator     │
            └──────────────────────┘
```

---

## Tech Stack

- **Framework**: Python 3.10+, Flask 3.0, Flask-CORS
- **Storage**: SQLite (`chatbot.db`)
- **NLP & Machine Learning**:
  - **NLTK**: Text normalization, tokenization, stopword removal, lemmatization.
  - **spaCy (`en_core_web_sm`)**: Named Entity Recognition (NER) & custom domain entity extraction (degrees, exams, campuses).
  - **Hugging Face Transformers (`facebook/bart-large-mnli`)**: Zero-shot intent classification into 15+ categories.
- **Containerization**: Docker & Docker Compose setup

---

## 15+ FAQ Intent Categories

1. `eligibility_criteria` - Marks, degree requirements, cutoffs.
2. `application_deadline` - Phase dates, application cutoff deadlines.
3. `fee_structure` - Tuition, course fees, development fees.
4. `scholarships` - Founder's scholarship, merit waivers, socio-economic aid.
5. `entrance_exam_details` - SRMJEEE syllabus, exam pattern, proctored test info.
6. `hostel_facilities` - AC/Non-AC rooms, mess, security, amenities.
7. `placement_statistics` - Recruiter lists, highest packages, job offers.
8. `campus_locations` - Kattankulathur, Ramapuram, Vadapalani, NCR, Amaravati.
9. `admission_process` - Registration, counseling, allotment steps.
10. `course_curriculum` - CBCS, electives, specializations, credits.
11. `document_verification` - Marksheets, certificates required.
12. `refund_policy` - UGC-compliant cancellation and refund rules.
13. `international_students` - Foreign/NRI student admissions.
14. `contact_support` - Phone numbers, email, helpdesk hours.
15. `general_greeting` - Welcome message and assistance.

---

## API Specifications

### 1. Health Check
- **Endpoint**: `GET /api/v1/health`
- **Response** (HTTP 200 OK):
```json
{
  "service": "SRM AI Admission Chatbot API",
  "status": "OK",
  "timestamp": "2026-08-22T09:51:00Z",
  "version": "1.0.0"
}
```

### 2. Chat Processing
- **Endpoint**: `POST /api/v1/chat`
- **Headers**: `Content-Type: application/json`
- **Request Body**:
```json
{
  "session_id": "user_session_123",
  "message": "What is the fee structure for B.Tech CSE at Kattankulathur campus?"
}
```
- **Response** (HTTP 200 OK):
```json
{
  "session_id": "user_session_123",
  "user_message": "What is the fee structure for B.Tech CSE at Kattankulathur campus?",
  "preprocessed_message": "fee structure btech cse kattankulathur campus",
  "intent": "fee_structure",
  "confidence": 0.9654,
  "entities": [
    {
      "end": 35,
      "label": "DEGREE_PROGRAM",
      "start": 25,
      "text": "B.Tech CSE"
    },
    {
      "end": 53,
      "label": "CAMPUS_LOCATION",
      "start": 39,
      "text": "Kattankulathur"
    }
  ],
  "bot_response": "The tuition fee for B.Tech programs at SRM IST ranges between ₹2,50,000 to ₹4,50,000 per year...",
  "timestamp": "2026-08-22T09:51:05Z"
}
```
- **Error Response** (HTTP 400 Bad Request):
```json
{
  "error": "Bad Request",
  "message": "'session_id' is required and must be a non-empty string."
}
```

### 3. Session History
- **Endpoint**: `GET /api/v1/history/<session_id>`
- **Response** (HTTP 200 OK):
```json
{
  "session_id": "user_session_123",
  "count": 1,
  "history": [
    {
      "id": 1,
      "session_id": "user_session_123",
      "user_message": "What is the fee structure for B.Tech CSE?",
      "intent": "fee_structure",
      "confidence": 0.9654,
      "bot_response": "The tuition fee for B.Tech programs at SRM IST...",
      "entities": [...],
      "timestamp": "2026-08-22T09:51:05Z"
    }
  ]
}
```

---

## Local Setup & Installation

### Prerequisites
- Python 3.10+
- Virtual environment (`venv`)

### Steps
1. **Clone the repository**:
   ```bash
   git clone <repository_url>
   cd ai_admission_chatbot
   ```

2. **Create and activate virtual environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate   # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r backend/requirements.txt
   ```

4. **Download NLTK and spaCy models**:
   ```bash
   python -m spacy download en_core_web_sm
   python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords'); nltk.download('wordnet'); nltk.download('punkt_tab')"
   ```

5. **Run the Application**:
   ```bash
   python backend/app.py
   ```
   The API & Web UI will start at `http://0.0.0.0:5000`.

---

## Running Automated Tests

Execute the backend unit test suite:
```bash
python -m unittest discover backend/tests
```

---

## Docker Deployment

### Build Docker Image
```bash
docker build -t srm-admission-chatbot:latest ./backend
```

### Run Container
```bash
docker run -d -p 5000:5000 --name srm_chatbot srm-admission-chatbot:latest
```

Verify container health:
```bash
curl http://localhost:5000/api/v1/health
```

---

## Repository Structure

```
.
├── backend/
│   ├── app.py              # Flask API application and routes
│   ├── database.py         # SQLite connection manager and CRUD handlers
│   ├── nlp_engine.py       # NLTK, spaCy NER, and HF Zero-Shot Classifier
│   ├── requirements.txt    # Project Python dependencies
│   ├── Dockerfile          # Docker image configuration
│   ├── .dockerignore       # Docker ignore rules
│   └── tests/
│       └── test_app.py     # Automated unit & integration tests
├── frontend/
│   ├── templates/
│   │   └── index.html      # SRM Admissions web portal template
│   └── static/
│       ├── css/
│       │   └── style.css   # Responsive portal stylesheet
│       └── js/
│           └── app.js      # Client side interactive JavaScript & API handler
├── docker-compose.yml      # Multi-container orchestration config
└── README.md               # Documentation & technical instructions
```
