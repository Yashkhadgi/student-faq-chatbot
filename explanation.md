# 🎓 SIT Nagpur EduBot - Technical Documentation & Evaluation Guide

This guide explains the 10 core modules implemented in this project, what they do, and exactly **where** in the codebase you can find and demonstrate them during your evaluation.

---

### Module 1: Rule-Based Logic (Foundational)
- **What it is:** Basic `if-else` and pattern matching for fixed college details (e.g., "Where is SIT?" -> "Nagpur Campus").
- **Explanation:** It handles high-priority institutional facts to provide instant answers without heavy NLP processing. If it hits an exact keyword, it bypasses the heavy AI models.
- **📍 Where to show this in code:** 
  - **File:** `modules/m01_basic_faq.py`
  - **Show:** The `basic_faq_lookup()` function. Show how it uses `score >= M01_FAST_PATH_SCORE` to skip everything else.

### Module 2: Text Preprocessing Pipeline
- **What it is:** Cleaning raw student queries.
- **Explanation:** Uses tokenization (splitting words), lower casing, and stopword removal (removing 'is', 'the'). This ensures "What are the fees?" and "FEES" are treated the same. It also uses TextBlob to fix typo spelling mistakes!
- **📍 Where to show this in code:** 
  - **File:** `modules/m02_preprocessor.py`
  - **Show:** The `preprocess()` function highlighting NLTK `word_tokenize`, removing English stopwords, and `blob.correct()` for spelling checks.

### Module 3: Semantic Synonym Mapping
- **What it is:** Keyword grouping.
- **Explanation:** Maps words like "Tuition", "Payment", and "Cost" to the specific "Fees" category using a dictionary, so the bot doesn't fail on different student vocabulary.
- **📍 Where to show this in code:** 
  - **File:** `modules/m03_synonym_expander.py`
  - **Show:** `expand_synonyms()` function loading from `data/synonyms.json` and adding mapped words securely to the user's query tokens.

### Module 4: Retrieval-based TF-IDF Similarity
- **What it is:** Mathematical text matching.
- **Explanation:** Uses Term Frequency-Inverse Document Frequency (TF-IDF) from `scikit-learn` to calculate a mathematical similarity score between the student's query and the FAQ database.
- **📍 Where to show this in code:** 
  - **File:** `modules/m04_tfidf_retrieval.py`
  - **Show:** How we use `TfidfVectorizer` and `cosine_similarity` to pull the highest scoring answer block. *Note: We optimized it to `fit` only once on load.*

### Module 5: Intent Classification
- **What it is:** Categorizing user goals via Machine Learning.
- **Explanation:** Defined 7+ intents (Admissions, Exams, Fees, etc.). The bot identifies the "Goal" of the user using an ML model trained on examples before searching for the answer.
- **📍 Where to show this in code:** 
  - **File:** `modules/m05_intent_classifier.py`
  - **Show:** The implementation of the ML `LogisticRegression` pipeline trained dynamically from `data/intents.json`.

### Module 6: Named Entity Recognition (NER)
- **What it is:** Extracting specific data points.
- **Explanation:** Extracts course codes (e.g., "CS", "ME"), departments, and semester years (e.g., "2nd Year") using Regex patterns so the bot captures exactly *what* the student is asking about.
- **📍 Where to show this in code:** 
  - **File:** `modules/m06_entity_extractor.py`
  - **Show:** The RegEx arrays `SEMESTER_REGEX`, `SIT_DEPT_REGEX`, and `COURSE_CODE_REGEX` inside the `extract_entities()` function.

### Module 7: Conversation State Management
- **What it is:** Context memory.
- **Explanation:** Supports multi-turn dialogue. The bot remembers what the user was talking about previously. If a student says "exam schedule" and then says "where?", it knows they mean the exam location.
- **📍 Where to show this in code:** 
  - **File:** `modules/m07_context_manager.py`
  - **Show:** The `enrich_with_context()` function prepending the previous intent to the current query.
  - **File:** `app.py` -> Point to `_sessions` dict, showing how every tab/user has a unique `session_id`.

### Module 8: Fallback & Human Handoff
- **What it is:** Error handling.
- **Explanation:** If the similarity score is below the threshold, the bot refuses to lie. It offers SIT Nagpur's official helpdesk email, phone, and WhatsApp instead of giving a wrong answer.
- **📍 Where to show this in code:** 
  - **File:** `modules/m08_fallback_handler.py` -> `handle_fallback()`
  - **File:** `config.py` -> Show `CONFIDENCE_THRESHOLD = 0.25` and the `FALLBACK_ESCALATE` WhatsApp link details.

### Module 9: Multi-Platform Mockup Logic
- **What it is:** Adaptive UI structure.
- **Explanation:** The backend generates pure JSON APIs. This allows one single robust backend engine to serve responses to completely different UI platforms (Web Chat vs WhatsApp phone sizes).
- **📍 Where to show this in code:** 
  - **File:** `app.py` -> Look at `@app.route("/api/chat")` and show it returns `jsonify({...})`.
  - **File:** `frontend/index.html` -> Show how Tab 1 (Web Chat) and Tab 2 (WhatsApp) look different but hit the *same* `/api/chat` API using JavaScript `fetch()`.

### Module 10: Continuous Learning & Logging
- **What it is:** Data-driven improvement.
- **Explanation:** Logs every single interaction (timestamp, query, intent, confidence score, session) so administrators can view unanswered queries and improve the chatbot.
- **📍 Where to show this in code:** 
  - **File:** `analytics/m10_analytics_logger.py` -> Show the `log_event()` CSV writer.
  - **File:** `frontend/index.html` -> Go to **Tab 3 (Analytics Dashboard)** to show the bar charts and tables reacting instantly to these server logs!

---

### 💡 Pro-Tip for Evaluation: The "Big Picture"
When the evaluator asks "How do these interact?", open **`app.py`** and scroll to the **`process_query()`** function. 

It proves to them that you orchestrated the entire pipeline step-by-step:
1. `m01_result` (M1: Fast Path Check)
2. `preprocess()` (M2: Text Cleaning)
3. `enrich_with_context()` (M7: Add previous memory)
4. `expand_synonyms()` (M3: Synonym Mapping)
5. `classify_intent()` (M5: ML Intent identification)
6. `extract_entities()` (M6: Regex Data Extraction)
7. `retrieve()` (M4: TF-IDF Search)
8. `handle_fallback()` (M8: Error routing)
9. `log_event()` (M10: Save Analytics)
