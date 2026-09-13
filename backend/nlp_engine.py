"""
NLP Engine for SRM AI Admission Chatbot.
Integrates NLTK for text preprocessing, spaCy for Named Entity Recognition (NER),
and Hugging Face Transformers (facebook/bart-large-mnli) for Zero-Shot Intent Classification.
"""

import re
import logging
from typing import List, Dict, Any, Tuple

# NLTK Setup
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

# spaCy Setup
import spacy

# Hugging Face Transformers Setup
from transformers import pipeline

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Safely download required NLTK resources
def download_nltk_resources():
    for resource in ["punkt", "punkt_tab", "stopwords", "wordnet"]:
        try:
            nltk.download(resource, quiet=True)
        except Exception as e:
            logger.warning(f"Could not download NLTK resource {resource}: {e}")

download_nltk_resources()

# Supported 15+ Intent categories
INTENTS = [
    "eligibility_criteria",
    "application_deadline",
    "fee_structure",
    "scholarships",
    "entrance_exam_details",
    "hostel_facilities",
    "placement_statistics",
    "campus_locations",
    "admission_process",
    "course_curriculum",
    "document_verification",
    "refund_policy",
    "international_students",
    "contact_support",
    "general_greeting",
]

# FAQ Response Repository with SRM Admission Information
FAQ_RESPONSES: Dict[str, str] = {
    "general_greeting": (
        "Hello! Welcome to the SRM Institute of Science and Technology Admission Portal. "
        "How can I assist you today with courses, fees, admissions, or entrance exams?"
    ),
    "eligibility_criteria": (
        "For B.Tech programs at SRM IST, candidates must have passed 10+2 (or equivalent) with a minimum of 50-60% aggregate "
        "in Physics, Mathematics, and Chemistry/Biotechnology/Biology/Computer Science. For PG programs like M.Tech, a relevant B.E/B.Tech degree is required."
    ),
    "application_deadline": (
        "The application deadline for SRMJEEE Phase 1 is typically in April, Phase 2 in June, and Phase 3 in July. "
        "Please visit the official SRM admissions portal (admissions.srmist.edu.in) to view exact cut-off dates for the current academic session."
    ),
    "fee_structure": (
        "The tuition fee for B.Tech programs at SRM IST ranges between ₹2,50,000 to ₹4,50,000 per year depending on the specialization "
        "(e.g., CSE, ECE, Mechanical) and campus location. Additional hostel and development fees apply."
    ),
    "scholarships": (
        "SRM IST offers several merit-based and financial scholarships: Founder's Scholarship (100% tuition waiver for top rankers in SRMJEEE/JEE Main), "
        "Sports Scholarships, Socio-Economic Scholarships, and Special Merit Scholarships for high achievers."
    ),
    "entrance_exam_details": (
        "Admissions to B.Tech programs are primarily based on the SRMJEEE (SRM Joint Engineering Entrance Examination), a remote proctored "
        "online test covering Physics, Chemistry, Mathematics/Biology, English, and Aptitude."
    ),
    "hostel_facilities": (
        "SRM offers separate AC and Non-AC hostels for male and female students across all campuses, featuring 24/7 security, high-speed Wi-Fi, "
        "gymnasiums, laundry facilities, and multi-cuisine mess options (North & South Indian)."
    ),
    "placement_statistics": (
        "SRM IST boasts exceptional placement records! Over 1,000+ top recruiter companies (including Microsoft, Amazon, Google, TCS, Cognizant) "
        "visit annually, offering 10,000+ placement offers with super dream packages reaching up to ₹1.1 Crore per annum."
    ),
    "campus_locations": (
        "SRM IST has primary campuses at Kattankulathur (Main Campus, Chennai), Ramapuram (Chennai), Vadapalani (Chennai), "
        "Tiruchirappalli (Tamil Nadu), Modinagar (NCR Delhi), and Amaravati (AP)."
    ),
    "admission_process": (
        "The admission process involves: 1) Register & Apply online at admissions.srmist.edu.in, 2) Appear for SRMJEEE or national exam, "
        "3) Participate in online counseling & program selection, 4) Pay admission fees & verify documents."
    ),
    "course_curriculum": (
        "SRM IST offers flexible Choice-Based Credit System (CBCS) curriculum updated regularly with industry leaders. Students can choose interdisciplinary electives, "
        "minor degrees, and complete capstone projects or industry internships."
    ),
    "document_verification": (
        "Required documents during enrollment include: 10th & 12th Grade Marksheets, SRMJEEE Scorecard, Transfer Certificate, Migration Certificate, "
        "Conduct Certificate, Category Certificate (if applicable), and Passport-size Photographs."
    ),
    "refund_policy": (
        "SRM IST adheres to standard UGC refund guidelines. Fees refunded prior to the commencement of classes incur a nominal handling fee, "
        "with tiered percentage deductions applicable after class commencement based on the withdrawal date."
    ),
    "international_students": (
        "SRM IST welcomes international applicants from over 50 countries! Dedicated NRI/International student admission desk, English proficiency assistance, "
        "and visa guidance are available at ir.admissions@srmist.edu.in."
    ),
    "contact_support": (
        "You can reach the SRM Directorate of Admissions via phone at +91-44-27455510 / +91-44-47437500 or email at admissions.india@srmist.edu.in. "
        "Helpdesk hours are Monday through Saturday, 9:00 AM to 5:00 PM."
    ),
}


class NLPEngine:
    """
    Encapsulated NLP Engine class incorporating text preprocessing (NLTK),
    Named Entity Recognition (spaCy), and Zero-Shot Intent Classification (Transformers).
    """

    def __init__(self, model_name: str = "facebook/bart-large-mnli"):
        self.lemmatizer = WordNetLemmatizer()
        try:
            self.stop_words = set(stopwords.words("english"))
        except Exception:
            self.stop_words = set()

        # Initialize spaCy
        self.nlp_spacy = self._load_spacy_model()

        # Lazy initialize HF zero-shot classifier
        self.model_name = model_name
        self._classifier_pipeline = None

    def _load_spacy_model(self):
        """Loads spacy model with fallback download if missing."""
        try:
            return spacy.load("en_core_web_sm")
        except Exception:
            logger.info("Downloading spaCy model 'en_core_web_sm'...")
            spacy.cli.download("en_core_web_sm")
            return spacy.load("en_core_web_sm")

    @property
    def classifier_pipeline(self):
        """Lazy load Hugging Face Zero-Shot Classification pipeline."""
        if self._classifier_pipeline is None:
            logger.info(f"Loading Hugging Face Zero-Shot Classifier model: {self.model_name}...")
            try:
                self._classifier_pipeline = pipeline(
                    "zero-shot-classification",
                    model=self.model_name
                )
            except Exception as e:
                logger.error(f"Failed to load HF pipeline: {e}")
                self._classifier_pipeline = None
        return self._classifier_pipeline

    def preprocess_text(self, text: str) -> str:
        """
        NLTK-based text preprocessing pipeline:
        - Lowercasing & noise removal
        - Tokenization
        - Stopword filtering
        - Lemmatization
        """
        if not text:
            return ""

        # Lowercase and retain alphanumeric characters and spaces
        cleaned_text = re.sub(r"[^a-zA-Z0-9\s]", "", text.lower())

        # Tokenization
        try:
            tokens = word_tokenize(cleaned_text)
        except Exception:
            tokens = cleaned_text.split()

        # Stopwords removal & Lemmatization
        filtered_tokens = [
            self.lemmatizer.lemmatize(token)
            for token in tokens
            if token not in self.stop_words
        ]

        return " ".join(filtered_tokens)

    def extract_entities(self, text: str) -> List[Dict[str, Any]]:
        """
        Extracts Named Entities using spaCy en_core_web_sm, supplemented
        with custom domain entity detection for SRM University.
        """
        if not text:
            return []

        doc = self.nlp_spacy(text)
        entities = []

        # Standard spaCy entities
        for ent in doc.ents:
            entities.append({
                "text": ent.text,
                "label": ent.label_,
                "start": ent.start_char,
                "end": ent.end_char
            })

        # Custom SRM Domain Entity Rules
        domain_patterns = [
            (r"\b(b\.?tech|m\.?tech|mba|mbbs|b\.?arch|phd|bca|mca)\b", "DEGREE_PROGRAM"),
            (r"\b(srmjeee|jee\s+main|gate|cat|neet|sat)\b", "ENTRANCE_EXAM"),
            (r"\b(kattankulathur|ramapuram|vadapalani|ncr|modinagar|amaravati|trichy)\b", "CAMPUS_LOCATION"),
            (r"\b(cse|ece|eee|mechanical|biotech|civil|data\s+science|ai\s+ml)\b", "BRANCH_SPECIALIZATION"),
        ]

        existing_texts = {e["text"].lower() for e in entities}
        for pattern, label in domain_patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                matched_str = match.group(0)
                if matched_str.lower() not in existing_texts:
                    entities.append({
                        "text": matched_str,
                        "label": label,
                        "start": match.start(),
                        "end": match.end()
                    })
                    existing_texts.add(matched_str.lower())

        return entities

    def classify_intent(self, text: str) -> Tuple[str, float]:
        """
        Classifies user query into one of 15+ FAQ intents using Hugging Face Zero-Shot pipeline.
        Includes a rule-based keyword fallback for robust fallback performance.
        """
        if not text or not text.strip():
            return "general_greeting", 1.0

        # Primary zero-shot classification using Hugging Face
        pipeline_obj = self.classifier_pipeline
        if pipeline_obj:
            try:
                hypothesis_template = "This user query is asking about SRM University {}."
                result = pipeline_obj(
                    text,
                    candidate_labels=INTENTS,
                    hypothesis_template=hypothesis_template
                )
                top_intent = result["labels"][0]
                confidence = float(result["scores"][0])
                return top_intent, round(confidence, 4)
            except Exception as e:
                logger.error(f"Error during HF zero-shot classification: {e}")

        # Rule-based fallback classifier if HF model unavailable or fails
        return self._keyword_fallback_intent(text)

    def _keyword_fallback_intent(self, text: str) -> Tuple[str, float]:
        """Keyword matching fallback for intent classification."""
        lowered = text.lower()

        keywords_map = {
            "general_greeting": ["hi", "hello", "hey", "greetings", "good morning", "good evening"],
            "eligibility_criteria": ["eligibility", "eligible", "qualification", "requirement", "cut off", "marks"],
            "application_deadline": ["deadline", "last date", "due date", "when to apply", "schedule"],
            "fee_structure": ["fee", "fees", "cost", "tuition", "charge", "payment", "price"],
            "scholarships": ["scholarship", "waiver", "concession", "financial aid", "stipend"],
            "entrance_exam_details": ["exam", "srmjeee", "syllabus", "test", "admit card", "pattern"],
            "hostel_facilities": ["hostel", "accommodation", "room", "mess", "food", "stay"],
            "placement_statistics": ["placement", "package", "salary", "job", "recruiter", "company"],
            "campus_locations": ["campus", "location", "address", "where is", "kattankulathur", "ramapuram"],
            "admission_process": ["admission", "how to apply", "process", "procedure", "seat allotment"],
            "course_curriculum": ["curriculum", "syllabus", "course", "subject", "credit", "branch"],
            "document_verification": ["document", "certificate", "verification", "marksheet", "proof"],
            "refund_policy": ["refund", "cancel admission", "withdraw", "cancellation"],
            "international_students": ["international", "nri", "foreign", "overseas"],
            "contact_support": ["contact", "phone", "email", "helpline", "support", "call"],
        }

        best_intent = "general_greeting"
        max_matches = 0

        for intent, kws in keywords_map.items():
            matches = sum(1 for kw in kws if kw in lowered)
            if matches > max_matches:
                max_matches = matches
                best_intent = intent

        confidence = 0.85 if max_matches > 0 else 0.50
        return best_intent, confidence

    def generate_response(self, intent: str, entities: List[Dict[str, Any]] = None) -> str:
        """
        Generates a dynamic answer based on the predicted intent and extracted entities.
        """
        base_response = FAQ_RESPONSES.get(
            intent,
            "Thank you for contacting SRM Admissions. For further details, please reach out to our admission helpdesk at admissions.india@srmist.edu.in."
        )

        # Dynamic entity context enhancement
        if entities:
            campuses = [e["text"] for e in entities if e.get("label") == "CAMPUS_LOCATION"]
            degrees = [e["text"] for e in entities if e.get("label") in ["DEGREE_PROGRAM", "BRANCH_SPECIALIZATION"]]

            addons = []
            if campuses:
                addons.append(f"Note for campus [{', '.join(campuses)}]: Specific campus guidelines apply.")
            if degrees:
                addons.append(f"Regarding program [{', '.join(degrees)}]: Seats are allocated based on merit & eligibility.")

            if addons:
                base_response += "\n\n" + " ".join(addons)

        return base_response

    def process_query(self, text: str) -> Dict[str, Any]:
        """
        Executes complete NLP pipeline: Preprocessing -> NER -> Zero-Shot Intent Classification -> Dynamic Response.
        """
        preprocessed = self.preprocess_text(text)
        entities = self.extract_entities(text)
        intent, confidence = self.classify_intent(text)
        bot_response = self.generate_response(intent, entities)

        return {
            "preprocessed_message": preprocessed,
            "intent": intent,
            "confidence": confidence,
            "entities": entities,
            "bot_response": bot_response
        }
