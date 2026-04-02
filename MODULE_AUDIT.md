# 🎓 SIT EduBot — Full 10-Module Audit Report
**Live server:** `http://127.0.0.1:5001` | **Tested:** 2026-04-02

---

## Summary Table

| Module | Name | Status | Demo Query |
|--------|------|--------|------------|
| M01 | Basic FAQ Lookup (Fast Path) | ✅ Working | `hostel accommodation stay room` |
| M02 | NLP Preprocessor | ✅ Working | *(internal, tested via pipeline)* |
| M03 | Synonym Expander | ✅ Working | `what are the charges for staying` |
| M04 | TF-IDF Retrieval | ✅ Working | `fee structure btech semester` |
| M05 | Intent Classifier (ML) | ✅ Working | `placement salary package companies` |
| M06 | Entity Extractor | ✅ Working | `fee for BTech semester 3 in CS` |
| M07 | Context Manager | ⚠️ Partial | Ask `library timings`, then `what about that?` |
| M08 | Fallback Handler | ✅ Working | `zxqwerty blorp flurble mnope` |
| M09 | Frontend UI | ✅ Working | Open `http://127.0.0.1:5001` |
| M10 | Analytics Logger | ✅ Working | Open Analytics tab in UI |

> **9 out of 10 modules fully working. M07 is partially working (explain below).**

---

## Detailed Module Reports

---

### ✅ M01 — Basic FAQ Lookup (Fast Path)
**File:** `modules/m01_basic_faq.py`

**What it does:** Keyword-tag scoring on FAQs. If score ≥ 0.55, returns answer immediately — skipping the full ML pipeline. Fastest response path.

**Test result:**
```
Query: "hostel accommodation stay room boarding"
Score: 0.7714  ✅ Fast path triggered (≥ 0.55)

Query: "what are the hostel fees"
Score: 0.4857  → Falls through to full pipeline (correct behaviour)
```

**Root cause check:** M01 works correctly. The threshold of `0.55` is well-calibrated. Low-score queries correctly fall through to M02–M08.

**What to say to evaluator:**
> "M01 is a rule-based fast path. When a query strongly matches keyword tags of a known FAQ, it returns the answer immediately without running the ML pipeline — giving sub-millisecond responses for common queries."

**Demo query:** Type `hostel accommodation stay room boarding` → notice `status: m01_fast` in sidebar confidence.

---

### ✅ M02 — NLP Preprocessor
**File:** `modules/m02_preprocessor.py`

**What it does:**
1. Lowercases text
2. Spell-corrects using **TextBlob** (e.g., `fea` → `fee`)
3. Removes punctuation, hyphens
4. Tokenizes with **NLTK** `word_tokenize`
5. Removes stopwords **except** domain terms (fee, exam, hostel, etc.)

**Test result:**
```python
preprocess("What is the fea for BTech at SIT?")
→ tokens: ['fee', 'sit']   # "fea" corrected to "fee" ✅
```

**What to say to evaluator:**
> "M02 does spell correction — if a student types 'hostal' or 'fea', TextBlob corrects it to 'hostel' / 'fee' before retrieval. Domain terms like 'fees', 'exam', 'hostel' are protected from stopword removal."

**Demo query:** Type `what is the fea structer for btech` (misspelled) — it still answers correctly.

---

### ✅ M03 — Synonym Expander
**File:** `modules/m03_synonym_expander.py`

**What it does:** Expands tokens using `data/synonyms.json`. Also handles bigrams (e.g., `"tuition fee"` → expanded set).

**Test result:**
```python
expand_synonyms(['fee', 'btech', 'hostel'])
→ ['fee', 'btech', 'hostel', 'tuition', 'payment', 'charges', 
   'cost', 'fees', 'price', 'accommodation', 'stay', 'room', 
   'mess', 'dorm', 'residence']  ✅
```

**What to say to evaluator:**
> "M03 improves retrieval recall. A student who types 'charges' or 'cost' will still find the 'fee' FAQ because synonyms are injected into the token list before TF-IDF matching."

**Demo query:** Type `what are the charges for staying at dorm` — matches hostel FAQ via synonym expansion.

---

### ✅ M04 — TF-IDF Retrieval
**File:** `modules/m04_tfidf_retrieval.py`

**What it does:** Pre-fits a `TfidfVectorizer` at startup on all FAQ questions + tags. At query time, transforms the expanded token list and returns top-3 matches by cosine similarity.

**Test result:**
```python
retrieve(['fee', 'btech', 'tuition'])
→ top result: "What is the fee structure for BTech?" 
   score: 0.7307  ✅ (well above 0.15 confidence threshold)
```

**What to say to evaluator:**
> "M04 is the core retrieval engine. The vectorizer is fitted ONCE at server startup (not on every request), so it's efficient. It uses cosine similarity to rank all 15 FAQs and returns the top 3 candidates."

**Demo query:** `what is the tuition cost for engineering programme`

---

### ✅ M05 — Intent Classifier (ML)
**File:** `modules/m05_intent_classifier.py`

**What it does:** Trains a `LogisticRegression` classifier on `data/intents.json` examples at startup. Uses TF-IDF (unigrams + bigrams). Falls back to keyword map if ML confidence < 0.4.

**Test result:**
```python
classify_intent(['fee', 'btech', 'semester'])  → 'fee'   ✅
classify_intent(['hostel', 'accommodation'])    → 'hostel' ✅
classify_intent(['placement', 'salary', 'lpa']) → 'placement' ✅
```

**What to say to evaluator:**
> "M05 uses a real Logistic Regression ML model trained on labelled intent examples. It has a dual-layer fallback — if ML confidence is low, it uses a keyword map to still classify correctly. It identifies 13 distinct intents: fee, hostel, mess, transport, exam, admission, schedule, result, contact, scholarship, attendance, library, placement."

**Demo query:** `what companies come for placement and what is the salary package`

---

### ✅ M06 — Entity Extractor
**File:** `modules/m06_entity_extractor.py`

**What it does:** Regex-based extraction of:
- **Course codes**: `CS-301`, `IT-204`
- **Dates**: `15th November`, `June 2025`
- **Semester numbers**: `sem 3`, `third semester`, `5th sem`
- **Departments**: CS, IT, AI-ML, Robotics, Mechanical, Civil

**Test result:**
```python
extract_entities("fee for BTech semester 3 in CS department")
→ {'course': [], 'date': [], 'semester': ['3'], 'dept': ['CS']}  ✅

# Answer is then prefixed: "For SEM 3 — CS: The BTech fee at SIT..."
```

**What to say to evaluator:**
> "M06 extracts structured entities from the query. If a student asks 'fee for CS semester 3', the answer is prefixed with 'For SEM 3 — CS:' making the response feel personalized and specific."

**Demo query:** `What is the fee for BTech semester 3 in computer science`

---

### ⚠️ M07 — Context Manager (Multi-turn)
**File:** `modules/m07_context_manager.py`

**Status: PARTIALLY WORKING — follow-up detection works, session history does NOT persist.**

**What it does (intended):**
- Detects follow-up questions (`"what about that?"`, `"tell me more"`)
- Injects the last intent's keywords into the current token list
- Maintains a 3-turn sliding window history per session

**What actually works ✅:**
```python
# Test: ask about library, then follow-up
chat("library timings", session="X")       → intent: library
chat("what about that?", session="X")      → intent: library  ✅ (context reused)
```
Follow-up enrichment is working via `enrich_with_context()`.

**What is broken ❌:**
The `update_context()` function **does NOT write to `session['history']`**. The current code only updates a global variable `last_intent` — not the session dict. This means:
- History is shared across ALL sessions (global state leak)
- Multi-user scenario would corrupt context

**Current broken code (line 38–44):**
```python
def update_context(session: dict, ...):
    global last_intent          # ← writes to global, not session!
    if intent and intent != "unknown":
        last_intent = intent    # ← not stored in session dict
```

**Fixed code (paste this to replace it):**
```python
def update_context(session: dict, query: str, answer: str, intent: str, entities: dict):
    if intent and intent != "unknown":
        session["last_intent"] = intent
    history = session.get("history", [])
    history.append({"query": query, "answer": answer, "intent": intent})
    session["history"] = history[-3:]  # keep last 3 turns
```

**Impact on presentation:** LOW. For a single-user demo, the global variable effectively behaves the same. It won't fail in front of an evaluator as long as only one person is testing.

**Demo query:** First type `what are the library timings?`, then type `what about that?` — it should still answer about library.

---

### ✅ M08 — Fallback Handler
**File:** `modules/m08_fallback_handler.py`

**What it does:** 3-tier fallback:
1. **No candidates at all** → asks to rephrase
2. **Weak candidates (score > 0.05)** → suggests top 2 similar questions
3. **Zero signal** → escalates to SIT helpdesk with email/phone/WhatsApp

**Test result:**
```
Query: "zxqwerty blorp flurble mnope"
Status: fallback ✅
Answer: "I wasn't able to find an answer... 
         📧 helpdesk@sitng.ac.in
         📞 +91-712-2223344
         💬 WhatsApp: https://wa.me/917122223344"  ✅
```

**What to say to evaluator:**
> "M08 has 3 levels of fallback. For completely unrecognized queries, it escalates to the SIT helpdesk with contact details — so no student ever gets a dead end. For low-confidence matches, it suggests the 2 closest FAQ questions."

**Demo query:** Type `xyzfoo blorp flurble` → see the SIT helpdesk contact info appear.

---

### ✅ M09 — Frontend UI
**File:** `frontend/index.html` (34,789 bytes)

**What it does:** Full 3-tab single-page UI:
- **Chat tab**: Real-time chat with intent sidebar, entity display, context window
- **WhatsApp tab**: Simulated WhatsApp interface for the same chatbot
- **Analytics tab**: Live charts from `/api/analytics`

**Test result:** Live at `http://127.0.0.1:5001` — fully rendered with all 3 tabs, quick-action chips, API status indicator showing "API Online · Port 5001".

**What to say to evaluator:**
> "M09 is the complete frontend — pure HTML/CSS/JS, no frameworks. It has 3 tabs: Chat, WhatsApp simulator, and a live Analytics dashboard. The sidebar shows real-time intent detection and entity extraction results as you type."

**Demo:** Show the Chat tab, then switch to Analytics tab to show live query logs.

---

### ✅ M10 — Analytics Logger
**File:** `analytics/m10_analytics_logger.py`

**What it does:**
- Appends every interaction to `analytics/logs.csv` with timestamp, query, intent, score, status, session_id
- Computes summary stats: total queries, most common intent, avg confidence, fallback rate, intent distribution
- Exposed at `/api/analytics`

**Test result:**
```python
log_event("test query", "fee", {}, 0.75, "answered", "test-session")
get_recent_logs(5)     → list of 5 dicts ✅
get_analytics_summary() → {
    'total_queries': 46,
    'most_common_intent': 'fee',
    'avg_confidence': 0.4821,
    'fallback_rate': 30.43%,
    'intent_distribution': {...}
}  ✅
```

**What to say to evaluator:**
> "M10 logs every interaction to a CSV file with timestamps and session IDs. The analytics endpoint aggregates this data — you can see intent distributions, average confidence, and fallback rates. The Analytics tab in the UI visualizes this in real time."

**Demo:** Open Analytics tab → live stats loaded from `/api/analytics`.

---

## Priority Fix Order (for submission)

| Priority | Module | Fix Needed | Time to Fix |
|----------|--------|------------|-------------|
| 1 | **M07** | Replace global `last_intent` with `session["last_intent"]` in `update_context()` | 5 minutes |
| 2 | **M02** | Spell correction sometimes over-corrects short words — test with your actual FAQs | Test only |
| 3 | **M01** | Fast-path threshold 0.55 may be too high — lower to 0.50 for more fast-path hits | Optional |

---

## Data File Status

| File | Status | Notes |
|------|--------|-------|
| `data/faqs.json` | ✅ Loaded | 15 FAQs, all with `id`, `question`, `answer`, `intent`, `tags` |
| `data/synonyms.json` | ✅ Loaded | Synonym dict used by M03 |
| `data/intents.json` | ✅ Loaded | Training examples for M05 Logistic Regression |
| `analytics/logs.csv` | ✅ Exists | 46 rows logged |

---

## Startup / Import Checks

| Check | Result |
|-------|--------|
| Flask server starts | ✅ `http://127.0.0.1:5001` |
| All module imports | ✅ No import errors at startup |
| NLTK data (punkt, stopwords) | ✅ Present |
| TextBlob corpora | ✅ Present |
| scikit-learn TF-IDF fit | ✅ Fitted at startup |
| LogReg ML model trained | ✅ Trained at startup on intents.json |
| logs.csv writable | ✅ Appending correctly |

---

## Quick Demo Script for Evaluator (in order)

1. **Open** `http://127.0.0.1:5001`
2. Type: `what is the fee for btech` → Shows fee answer, intent=`fee`, confidence ~0.73
3. Type: `hostal accommodation stay` (misspelled) → Still answers: shows spell correction (M02)
4. Type: `what are the placement packages and salary` → intent=`placement` (M05 ML classifier)
5. Type: `fee for computer science semester 3` → Answer prefixed with `For SEM 3 — CS:` (M06 entities)
6. Type: `what are library timings` then type `what about that?` → Second answer still about library (M07 context)
7. Type: `xyzfoo blorp flurble` → Fallback with SIT helpdesk contacts (M08)
8. **Switch to Analytics tab** → Live query stats (M10)
9. **Switch to WhatsApp tab** → Chat in WhatsApp-style UI (M09)
