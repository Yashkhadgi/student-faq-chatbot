# 🎓 SIT EduBot — Student FAQ Chatbot

**Symbiosis Institute of Technology (SIT), Nagpur**

> An intelligent, multi-module FAQ chatbot that helps students at SIT Nagpur get
> quick answers about admissions, fees, exams, hostel, scholarships, and more.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    SIT EduBot — System                      │
│                                                             │
│  Browser (frontend/index.html)                              │
│     │  fetch() POST /api/chat                               │
│     ▼                                                       │
│  Flask app.py  ──▶  M01 Fast Path (keyword score ≥ 0.8)    │
│     │                      └──▶ RETURN immediately          │
│     ▼                                                       │
│  M02 Preprocess (NLTK tokenize + stopword + spellcheck)     │
│     ▼                                                       │
│  M07 Enrich with context (follow-up detection)              │
│     ▼                                                       │
│  M03 Synonym Expansion                                      │
│     ▼                                                       │
│  M05 Intent Classification (TF-IDF + Logistic Regression)   │
│     ▼                                                       │
│  M06 Entity Extraction (course, date, semester, dept)       │
│     ▼                                                       │
│  M04 TF-IDF Retrieval (pre-fitted vectorizer)               │
│     ▼                                                       │
│  Confidence ≥ 0.25? ──Yes──▶ Return answer                  │
│     └──No──▶ M08 Fallback (suggestions + SIT helpdesk)     │
│     ▼                                                       │
│  M07 Update Context  ──▶  M10 Log Event (logs.csv)          │
└─────────────────────────────────────────────────────────────┘
```

---

## Tech Stack

| Layer     | Technology |
|-----------|-----------|
| Backend   | Python 3.10+, Flask 3.0 |
| ML        | scikit-learn (TF-IDF, Logistic Regression) |
| NLP       | NLTK (tokenize, stopwords), TextBlob (spelling) |
| Frontend  | Pure HTML5 + Vanilla CSS + Vanilla JS (no frameworks) |
| Logging   | CSV via Python's `csv` module |
| Tests     | pytest |

---

## Project Structure

```
student-faq-chatbot/
├── app.py                  # Flask REST API + pipeline orchestrator
├── config.py               # Central config (paths, thresholds, contacts)
├── requirements.txt
├── README.md
├── data/
│   ├── faqs.json           # 15 SIT Nagpur FAQs
│   ├── intents.json        # Intent labels + training examples
│   └── synonyms.json       # Synonym dictionary
├── modules/
│   ├── m01_basic_faq.py    # Rule-based fast-path (cached, keyword-scored)
│   ├── m02_preprocessor.py # Full NLP pipeline (NLTK + TextBlob)
│   ├── m03_synonym_expander.py
│   ├── m04_tfidf_retrieval.py  # Pre-fitted TF-IDF retrieval
│   ├── m05_intent_classifier.py # ML classifier (TF-IDF + LogReg)
│   ├── m06_entity_extractor.py  # Course, semester, dept, date
│   ├── m07_context_manager.py   # Multi-turn session state
│   └── m08_fallback_handler.py  # Clarification + SIT escalation
├── frontend/
│   └── index.html          # 3-tab UI (Chat + WhatsApp + Analytics)
├── analytics/
│   ├── m10_analytics_logger.py
│   └── logs.csv
├── utils/
│   ├── helpers.py          # JSON data loaders
│   └── logger.py
└── tests/
    ├── test_m01.py through test_m08.py
```

---

## Installation

### 1. Clone the repository
```bash
git clone <repo-url>
cd student-faq-chatbot
```

### 2. Create a virtual environment
```bash
python3 -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Download NLTK data (one-time)
```bash
python -c "import nltk; nltk.download('punkt'); nltk.download('punkt_tab'); nltk.download('stopwords')"
```

### 5. Download TextBlob corpora (one-time)
```bash
python -m textblob.download_corpora
```

---

## Running the App

### Start the Flask server
```bash
python app.py
```
The server starts at **http://localhost:5000**

- Open **http://localhost:5000** in your browser for the full UI
- Or open `frontend/index.html` directly (the app calls `localhost:5000` for API)

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET`  | `/`      | Serves the frontend UI |
| `GET`  | `/api/health` | Health check → `{"status": "ok"}` |
| `GET`  | `/api/faqs` | Returns all 15 FAQ questions |
| `POST` | `/api/chat` | Send a query, get a chatbot response |
| `GET`  | `/api/analytics` | Returns last 50 logs + summary stats |

### POST /api/chat

**Request:**
```json
{
  "query": "What is the fee for BTech?",
  "session_id": "abc-123"
}
```

**Response:**
```json
{
  "answer": "The BTech fee at SIT Nagpur is ₹1,20,000 per semester...",
  "intent": "fee",
  "entities": { "course": [], "date": [], "semester": [], "dept": [] },
  "status": "answered",
  "confidence": 0.7431,
  "top_matches": [...],
  "session_id": "abc-123"
}
```

---

## Running Tests

```bash
pytest tests/ -v
```

---

## Module Descriptions

| Module | File | Description |
|--------|------|-------------|
| **M01** | `m01_basic_faq.py` | Tag-based keyword scoring, cached FAQ lookup. Fast path if score ≥ 0.8 |
| **M02** | `m02_preprocessor.py` | NLTK tokenization, domain-aware stopword removal, TextBlob spell correction |
| **M03** | `m03_synonym_expander.py` | Synonym dictionary expansion to improve retrieval recall |
| **M04** | `m04_tfidf_retrieval.py` | TF-IDF + cosine similarity, vectorizer fitted once at startup |
| **M05** | `m05_intent_classifier.py` | TF-IDF + Logistic Regression trained on `intents.json` |
| **M06** | `m06_entity_extractor.py` | Regex + dict-based extraction of course codes, semesters, departments |
| **M07** | `m07_context_manager.py` | Multi-turn context: follow-up detection, sliding window (3 turns) |
| **M08** | `m08_fallback_handler.py` | Clarification → suggestions → SIT helpdesk escalation |
| **M09** | `frontend/index.html` | Chat UI + WhatsApp simulator + Analytics Dashboard |
| **M10** | `m10_analytics_logger.py` | CSV event logging with summary stats (intent dist., fallback rate) |

---

## Contact / Helpdesk

- 📧 **helpdesk@sitng.ac.in**
- 📞 **+91-712-2223344**
- 💬 **WhatsApp:** https://wa.me/917122223344
- 🕐 Office hours: Mon–Sat, 9AM–5PM

---

*Built as part of the NLP/AI curriculum project at SIT Nagpur.*
