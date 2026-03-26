# SIT EduBot – Complete Project Report
**Symbiosis Institute of Technology, Nagpur | Student FAQ Chatbot**
**Date:** 2026-03-26 | **Server:** http://localhost:5001 | **GitHub:** https://github.com/Yashkhadgi/student-faq-chatbot

---

## 1. Project Overview

A production-ready Student FAQ Chatbot for SIT Nagpur built as a **Flask REST API** with a single-file **HTML/CSS/JS frontend**. The architecture is a 10-module NLP pipeline that processes student queries and returns intelligent answers from a FAQ database.

- **Backend Language:** Python 3.14
- **Web Framework:** Flask 3.0.2 + Flask-CORS 4.0.0
- **NLP Libraries:** scikit-learn (TF-IDF), NLTK (tokenizer/stopwords), TextBlob (spelling)
- **Frontend:** Vanilla HTML/CSS/JS (no frameworks), Google Fonts (Inter)
- **Port:** 5001 (5000 is blocked by macOS AirPlay Receiver on this machine)
- **Run Command:** `source venv/bin/activate && python app.py`

---

## 2. Project File Structure

```
student-faq-chatbot/
├── app.py                          # Flask REST API + 10-module pipeline orchestrator
├── config.py                       # All constants, paths, thresholds
├── requirements.txt                # Python dependencies
├── explanation.md                  # Module-by-module explanation for evaluation
├── PROJECT_REPORT.md               # This file
│
├── data/
│   ├── faqs.json                   # 15 SIT Nagpur FAQ entries (source of truth)
│   ├── synonyms.json               # Synonym dictionary for Module 3
│   └── intents.json                # Intent training examples for Module 5 ML model
│
├── modules/
│   ├── m01_basic_faq.py            # Module 1: Rule-based keyword fast path
│   ├── m02_preprocessor.py         # Module 2: NLTK text preprocessing pipeline
│   ├── m03_synonym_expander.py     # Module 3: Synonym/keyword mapping
│   ├── m04_tfidf_retrieval.py      # Module 4: TF-IDF cosine similarity retrieval
│   ├── m05_intent_classifier.py    # Module 5: ML intent classification (LogReg)
│   ├── m06_entity_extractor.py     # Module 6: Named Entity Recognition (Regex)
│   ├── m07_context_manager.py      # Module 7: Conversation state / last_intent
│   └── m08_fallback_handler.py     # Module 8: Fallback + SIT helpdesk routing
│
├── analytics/
│   ├── m10_analytics_logger.py     # Module 10: CSV logger + summary stats
│   └── logs.csv                    # Runtime log (gitignored)
│
├── frontend/
│   └── index.html                  # 3-tab UI: Chat + WhatsApp + Analytics (single file)
│
├── tests/
│   ├── test_m01.py to test_m08.py  # 51 pytest test cases covering all modules
│
└── utils/
    └── helpers.py                  # load_faqs(), load_synonyms(), load_intents()
```

---

## 3. config.py – All Configurable Constants

```python
FAQ_PATH        = "data/faqs.json"
SYNONYMS_PATH   = "data/synonyms.json"
INTENTS_PATH    = "data/intents.json"
ANALYTICS_LOG   = "analytics/logs.csv"
FRONTEND_DIR    = "frontend/"

TFIDF_TOP_N          = 3      # Return top 3 FAQ matches
CONFIDENCE_THRESHOLD = 0.2    # Below this → trigger Module 8 fallback
M01_FAST_PATH_SCORE  = 0.8    # Above this → skip TF-IDF, return M01 answer directly
CONTEXT_WINDOW       = 3      # Keep last 3 turns in session history

FLASK_HOST = "0.0.0.0"
FLASK_PORT = 5001
FLASK_DEBUG = True
```

---

## 4. Flask API Endpoints (app.py)

| Method | Route | Description |
|--------|-------|-------------|
| GET  | `/` | Serves `frontend/index.html` |
| GET  | `/api/health` | `{"status": "ok", "service": "SIT EduBot"}` |
| GET  | `/api/faqs` | Returns all 15 FAQ questions as JSON |
| POST | `/api/chat` | Main chat endpoint — runs full 10-module pipeline |
| GET  | `/api/analytics?limit=50` | Returns last N logs + summary statistics |

**POST `/api/chat` Request:**
```json
{ "query": "What are the BTech fees?", "session_id": "uuid-here" }
```

**POST `/api/chat` Response:**
```json
{
  "answer": "The BTech fee at SIT Nagpur is ₹1,20,000 per semester...",
  "intent": "fee",
  "confidence": 0.269,
  "status": "answered",
  "entities": { "course": [], "dept": [], "semester": [], "date": [] },
  "top_matches": [...],
  "session_id": "uuid-here"
}
```

---

## 5. The 10-Module Pipeline (in execution order inside process_query())

### MODULE 1 – Rule-Based Fast Path (`modules/m01_basic_faq.py`)
- **What it does:** On every request, scores the query against all 15 FAQs using keyword/tag overlap scoring.
- **Key logic:** Each FAQ has a `tags` array. Score = `hits / len(tags) + 0.2 bonus` if question words match.
- **Fast path:** If `score >= M01_FAST_PATH_SCORE (0.8)`, immediately returns the answer and **skips all other modules** (M02–M07).
- **Why:** Saves compute for obvious keyword-match questions.
- **Key function:** `basic_faq_lookup(query)` → returns `{faq: {...}, score: float}` or `None`

---

### MODULE 2 – Text Preprocessing (`modules/m02_preprocessor.py`)
- **What it does:** Cleans and normalizes raw student input using a full NLP pipeline.
- **Steps:**
  1. Lowercase
  2. TextBlob spelling correction (`blob.correct()`)
  3. Punctuation removal (preserves hyphens in course codes like `CS-301`)
  4. NLTK `word_tokenize()`
  5. Stopword removal using NLTK English stopwords **minus** domain words (fees, exam, hostel, etc.)
- **Domain protection:** Words like `fee`, `exam`, `hostel` are NEVER removed even if they appear in NLTK's stopword list.
- **Key function:** `preprocess(raw_query)` → returns `{tokens: [...], cleaned: "string"}`

---

### MODULE 3 – Synonym Expander (`modules/m03_synonym_expander.py`)
- **What it does:** Expands query tokens with their SIT-specific synonyms before TF-IDF search.
- **Data source:** `data/synonyms.json` — includes:
  - `fee` → ["tuition", "payment", "charges", "cost", "fees", "price"]
  - `admission` → ["join", "entrance", "enrollment", "apply", "registration"]
  - `hostel` → ["accommodation", "stay", "room", "mess", "dorm", "residence"]
- **Key function:** `expand_synonyms(tokens)` → returns deduplicated expanded token list

---

### MODULE 4 – TF-IDF Retrieval (`modules/m04_tfidf_retrieval.py`)
- **What it does:** Finds the most mathematically similar FAQ to the expanded query.
- **Optimization:** The `TfidfVectorizer` is **fitted once at module load** on all FAQ questions + tags. At query time, only `transform()` is called (not `fit_transform()`), which is much faster.
- **Corpus:** Each FAQ's question text concatenated with its tags.
- **Scoring:** `cosine_similarity(query_vector, faq_matrix)` from scikit-learn.
- **Returns:** Top 3 FAQs sorted by cosine similarity score (0.0–1.0).
- **Key function:** `retrieve(tokens)` → returns list of `{id, question, answer, intent, score}`

---

### MODULE 5 – Intent Classifier (`modules/m05_intent_classifier.py`)
- **What it does:** Classifies the user's intent into one of 9+ categories using Machine Learning.
- **Model:** `TfidfVectorizer (ngram_range=(1,2))` + `LogisticRegression (C=5.0)` — trained at module load from `data/intents.json`.
- **Intents:** fee, exam, admission, hostel, schedule, result, contact, scholarship, attendance
- **Fallback:** If ML confidence < 0.5, falls back to keyword matching.
- **Key function:** `classify_intent(tokens)` → returns intent string

---

### MODULE 6 – Entity Extractor (`modules/m06_entity_extractor.py`)
- **What it does:** Extracts structured data points from the raw query using regular expressions.
- **Extracts:**
  - `course` — Pattern `[A-Za-z]{2,5}-\d{3}` (e.g., CS-301, IT-204)
  - `semester` — "sem 3", "3rd semester", "third sem" (maps ordinals 1st–8th)
  - `dept` — CS, IT, Robotics, AI-ML, Mechanical, Civil
  - `date` — "15th November", "June 2025", etc.
- **Enrichment:** `enrich_answer_with_entities()` prepends entity context to answers (e.g., "For SEM 3 — CS: The fee is...")
- **Key function:** `extract_entities(raw_query)` → returns `{course, date, semester, dept}`

---

### MODULE 7 – Context Manager (`modules/m07_context_manager.py`)
- **What it does:** Enables multi-turn conversation by remembering the last conversation intent.
- **Implementation:** Uses a **global variable** `last_intent = "unknown"` that persists across requests.
- **Follow-up detection:** Checks if query contains trigger words: "that", "it", "this", "same", "also", "tell me more", etc.
- **Enrichment:** If follow-up is detected, appends `last_intent` as a pseudo-token to the query tokens before TF-IDF search.
- **Key functions:**
  - `enrich_with_context(raw_query, tokens, session)` → returns enriched tokens
  - `update_context(session, query, answer, intent, entities)` → updates global `last_intent`

---

### MODULE 8 – Fallback Handler (`modules/m08_fallback_handler.py`)
- **What it does:** Handles cases where TF-IDF confidence falls below `CONFIDENCE_THRESHOLD (0.2)`.
- **3-tier strategy:**
  1. No candidates at all → asks user to rephrase
  2. Low-confidence candidates (score > 0.05) → suggests top 2 similar questions
  3. Nothing relevant → escalates to official SIT Nagpur contacts
- **SIT Nagpur Escalation Contact:**
  - 📧 helpdesk@sitng.ac.in
  - 📞 +91-712-2223344
  - 💬 WhatsApp: https://wa.me/917122223344
  - Office: Mon–Sat, 9AM–5PM
- **Key function:** `handle_fallback(query, candidates)` → returns fallback string

---

### MODULE 9 – Multi-Platform Mockup (Frontend Architecture)
- **What it does:** The backend returns pure JSON, which is consumed by two completely different UIs in the same `frontend/index.html` file.
- **Tab 1 (Web Chat):** Dark navy theme (#0A1628), left sidebar with live intent/entity/context display, animated typing dots, quick-reply chips.
- **Tab 2 (WhatsApp Simulator):** A phone frame (360x700px, 32px border-radius) with authentic WhatsApp colors (#1F2C34 header, #0D1821 background, #005C4B user bubbles, #00A884 send button). Uses same `/api/chat` endpoint with `_wa` suffix on session ID.
- **Tab 3 (Analytics Dashboard):** 4 KPI cards, pure-JS horizontal bar chart, logs table.
- **Key technical detail:** Both Tab 1 and Tab 2 call `fetch('/api/chat', ...)` — same backend, different UI.

---

### MODULE 10 – Analytics Logger (`analytics/m10_analytics_logger.py`)
- **What it does:** Logs every single interaction to `analytics/logs.csv` and provides summary statistics for the dashboard.
- **CSV Columns:** `timestamp, query, intent, score, response, session_id`
- **Summary stats returned by `get_analytics_summary()`:**
  - `total_queries` — count of all rows
  - `most_common_intent` — from Counter
  - `avg_confidence` — mean of all score values
  - `fallback_rate` — % of rows where response == "fallback"
  - `intent_distribution` — dict of intent → count
- **Key functions:**
  - `log_event(query, intent, entities, score, status, session_id)` — appends one row
  - `get_recent_logs(limit=50)` — returns last N rows as list of dicts
  - `get_analytics_summary()` — returns aggregate stats dict

---

## 6. Frontend (frontend/index.html)

**Single self-contained file — all CSS and JS embedded inline.**

### Design System
| Variable | Value | Usage |
|----------|-------|-------|
| Background | `#0A1628` | Page background |
| Surface | `#0D1F3C` | Cards, sidebar, inputs |
| Border | `#1E3A5F` | All borders |
| Accent | `#FF6B35` | Logo, send button, active tab, progress bar |
| Bot bubble | `#162D4E` bg, `#C8D8EE` text | Bot messages |
| User bubble | `#E8EEFF` bg, `#1A2640` text | User messages |
| Info blue | `#7EB8F7` | Entity tags, muted headings |
| Muted | `#5A7FA8` | Timestamps, labels |
| Font | Inter (Google Fonts) | All text |

### Key JS Functions
| Function | Description |
|----------|-------------|
| `sendChat()` | Sends POST to `/api/chat`, shows typing dots, renders response |
| `sendWa()` | WhatsApp-style version of sendChat |
| `updateSidebar(data, query)` | Updates intent badge, confidence bar, entity pills, context |
| `renderMsg(sender, text, isError)` | Creates and appends a message bubble to the chat list |
| `refreshAnalytics()` | Fetches GET `/api/analytics`, updates KPI cards, chart, table |
| `showTab(id)` | Switches between the 3 tab panels |

### Session ID
- Generated on page load: `"sess-" + Math.random().toString(36).substr(2, 9)`
- Reused for all requests in the Chat tab
- WhatsApp uses same session + `"_wa"` suffix

### Analytics Auto-Refresh
- Dashboard refreshes every **30 seconds** via `setInterval()` while the Analytics tab is active.

---

## 7. Data Files

### data/faqs.json (15 entries)
Each FAQ has: `id, question, answer, intent, tags[]`

| ID | Intent | Question |
|----|--------|----------|
| 1  | admission | Last date to submit admission form |
| 2  | fee | Fee structure for BTech |
| 3  | exam | Semester exam schedule |
| 4  | contact | Contact admissions office |
| 5  | admission | Documents required for admission |
| 6  | hostel | Hostel facility available? |
| 7  | attendance | Attendance requirement |
| 8  | scholarship | How to apply for scholarship |
| 9  | schedule | Timetable for CS-301 |
| 10 | result | Semester result announcement |
| 11 | library | Library timings |
| 12 | hostel | Single occupancy hostel fee |
| 13 | admission | Admission-related contact |
| 14 | exam | Exam date sheet location |
| 15 | scholarship | Scholarship application deadline |

### data/synonyms.json
```json
{
  "fee": ["tuition", "payment", "charges", "cost", "fees", "price"],
  "exam": ["test", "assessment", "evaluation", "paper", "examination"],
  "admission": ["join", "entrance", "enrollment", "apply", "registration", "admission"],
  "hostel": ["accommodation", "stay", "room", "mess", "dorm", "residence"],
  "schedule": ["timetable", "timing", "slots", "calendar", "routine"],
  "result": ["marks", "grades", "score", "performance", "outcome"],
  "contact": ["reach", "call", "email", "phone", "connect", "helpdesk"],
  "scholarship": ["financial aid", "grant", "stipend", "bursary", "award"],
  "attendance": ["presence", "participation", "regularity"],
  "documents": ["certificates", "papers", "proof", "records", "marksheet"]
}
```

### data/intents.json (9 intents × ~4 examples each)
Used to train the Logistic Regression model in M05. Labels: admission, fee, exam, schedule, contact, hostel, attendance, scholarship, result.

---

## 8. Test Suite

**Location:** `tests/` | **Framework:** pytest | **Total:** 51 tests — **all passing**

| File | Module | Key Test Cases |
|------|--------|----------------|
| test_m01.py | M01 | FAQ lookup returns correct FAQ, returns None for unknown, score ≥ 0 |
| test_m02.py | M02 | Lowercase, punctuation removal, stopword removal, preserves domain words |
| test_m03.py | M03 | Synonym expansion, deduplication, no mutation of original tokens |
| test_m04.py | M04 | Returns top-N results, scores between 0–1, fees query matches fee FAQ |
| test_m05.py | M05 | Classifies "fee structure" as fee, "hostel" as hostel, empty as unknown |
| test_m06.py | M06 | Extracts course codes, semester numbers, departments correctly |
| test_m07.py | M07 | Follow-up detection, context injection, non-follow-up unchanged |
| test_m08.py | M08 | Empty candidates → clarify, low score → suggestions, no match → escalate |

---

## 9. Known Issues & Notes

1. **Confidence Threshold:** Set to `0.2` (not `0.4`). TF-IDF cosine similarity on 15 short FAQ entries typically scores in the 0.2–0.4 range for good matches. Setting it higher causes valid answers to be classified as fallback.

2. **M07 Global State:** The `last_intent` variable is a Python module-level global. This means it is shared across ALL user sessions on the server. It works for demo purposes but in production should be moved to the per-session dict in `_sessions`.

3. **TextBlob Spelling:** Can be slow on first request (cold start). On subsequent requests it is fast. If speed is critical, disable by passing `correct_spelling=False` to `preprocess()`.

4. **Port Conflicts:** On macOS, AirPlay Receiver uses port 5000. The app always runs on **port 5001**. If the port is occupied by a zombie process, kill it with `kill $(lsof -ti :5001)`.

5. **Module 9 (WhatsApp Simulator):** This is a UI mockup only. It does not connect to the real WhatsApp Business API. It uses the same Flask `/api/chat` endpoint as the web chat.

---

## 10. How to Run Locally

```bash
# 1. Navigate to project
cd /Users/yashkhadgi/Desktop/student-faq-chatbot

# 2. Activate virtual environment
source venv/bin/activate

# 3. Install dependencies (if first time)
pip install -r requirements.txt

# 4. Run tests
pytest tests/ -v

# 5. Start server
python app.py

# 6. Open browser
# http://localhost:5001
```
