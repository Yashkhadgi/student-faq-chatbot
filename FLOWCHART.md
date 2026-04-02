# 🎓 SIT EduBot — Project Flowchart

## Full NLP Pipeline (M01 → M10)

```mermaid
flowchart TD
    A([👤 Student Types Query\nin Browser UI]) --> B

    subgraph M09["📱 M09 — Frontend UI · index.html"]
        B[/"Chat Tab / WhatsApp Tab"/]
    end

    B -->|POST /api/chat| C

    subgraph FLASK["⚙️ Flask app.py — Pipeline Orchestrator"]

        C[Receive raw_query + session_id]

        subgraph M01["🚀 M01 — Basic FAQ Lookup · m01_basic_faq.py"]
            D[Keyword Tag Scoring\nover 15 FAQs]
            E{Score ≥ 0.55?}
        end

        C --> D --> E

        E -->|Yes — Fast Path ⚡| Z1[Return Answer Immediately\nstatus = m01_fast]

        E -->|No — Full Pipeline| F

        subgraph M02["🔤 M02 — Preprocessor · m02_preprocessor.py"]
            F[Lowercase + Spell Correct\nvia TextBlob]
            F2[NLTK Tokenize\n+ Stopword Removal]
            F --> F2
        end

        subgraph M07A["🧠 M07 — Context Enrichment · m07_context_manager.py"]
            G[Detect Follow-up Triggers\ne.g. 'what about that?']
            G2[Inject Last Intent Keywords\ninto Token List]
            G --> G2
        end

        F2 --> G --> G2

        subgraph M03["🔁 M03 — Synonym Expander · m03_synonym_expander.py"]
            H[Expand Tokens via synonyms.json\ne.g. fee → tuition, charges, cost]
        end

        G2 --> H

        subgraph M05["🤖 M05 — Intent Classifier · m05_intent_classifier.py"]
            I[TF-IDF + Logistic Regression\nTrained on intents.json]
            I2{ML Confidence ≥ 0.4?}
            I3[Return ML Intent]
            I4[Keyword Fallback Map\n13 intents]
            I --> I2
            I2 -->|Yes| I3
            I2 -->|No| I4
        end

        H --> I

        subgraph M06["🏷️ M06 — Entity Extractor · m06_entity_extractor.py"]
            J[Regex Extract:\nCourse · Semester · Dept · Date]
            J2[Enrich Answer with Prefix\ne.g. 'For SEM 3 — CS:']
            J --> J2
        end

        I3 & I4 --> J

        subgraph M04["📊 M04 — TF-IDF Retrieval · m04_tfidf_retrieval.py"]
            K[Cosine Similarity\nvs Pre-fitted FAQ Matrix]
            K2[Return Top-3 Ranked FAQs\nwith Confidence Scores]
            K --> K2
        end

        J --> K

        subgraph THRESH["⚖️ Confidence Threshold Decision · app.py"]
            L{Top Score ≥ 0.15?}
        end

        K2 --> L

        L -->|Yes — Answered ✅| M[Return Best FAQ Answer\n+ Enrich with Entities M06]

        subgraph M08["🆘 M08 — Fallback Handler · m08_fallback_handler.py"]
            N{Any weak\ncandidates\nscore > 0.05?}
            N1[Suggest Top-2\nSimilar Questions]
            N2[Escalate to SIT Helpdesk\n📧 helpdesk@sitng.ac.in\n📞 +91-712-2223344]
            N -->|Yes| N1
            N -->|No| N2
        end

        L -->|No — Fallback ⚠️| N

        subgraph M07B["🧠 M07 — Update Context · m07_context_manager.py"]
            O[Store Intent + Turn\nin Session History\nSliding Window = 3]
        end

        M & N1 & N2 --> O

        subgraph M10["📈 M10 — Analytics Logger · m10_analytics_logger.py"]
            P[Append to logs.csv\ntimestamp · query · intent · score · status]
            P2[Fallback? → Also write\nto unanswered_logs.json]
            P --> P2
        end

        O --> P
    end

    P --> Q[/"JSON Response:\nanswer · intent · entities\nconfidence · status · session_id"/]
    Z1 --> Q

    Q -->|Render in browser| R

    subgraph M09B["📱 M09 — Frontend Renders Response"]
        R[Chat Bubble + Sidebar Update\nIntent · Confidence · Entities · Context]
        R2[Analytics Tab: GET /api/analytics\nLive Stats from M10]
    end

    R --> S([✅ Student sees Answer])
```

---

## Fast Path vs Full Pipeline

```mermaid
flowchart LR
    A[User Query] --> B{M01 Score\n≥ 0.55?}
    
    B -->|YES ⚡ Fast Path| C[Skip M02→M07\nReturn in ~1ms]
    B -->|NO 🔄 Full Pipeline| D[M02 → M03 → M05 → M06 → M04]
    
    D --> E{Confidence\n≥ 0.15?}
    E -->|YES ✅| F[Return Answer]
    E -->|NO ⚠️| G[M08 Fallback]

    style C fill:#2d6a4f,color:#fff
    style F fill:#2d6a4f,color:#fff
    style G fill:#9b2226,color:#fff
```

---

## M08 Three-Tier Fallback

```mermaid
flowchart TD
    A[Query Could Not Be Answered] --> B{Any TF-IDF\ncandidates returned?}
    
    B -->|No candidates| C["🔁 Tier 1: Ask to Rephrase\n'Could you rephrase? Try: fees, hostel, exams...'"]
    
    B -->|Weak candidates exist\nscore > 0.05| D["💡 Tier 2: Suggest Similar Questions\n'Did you mean one of these?\n1. What is the fee for BTech?\n2. What are hostel charges?'"]
    
    B -->|Candidates exist\nbut all score = 0| E["📞 Tier 3: Escalate to SIT Helpdesk\n📧 helpdesk@sitng.ac.in\n📞 +91-712-2223344\n💬 WhatsApp: wa.me/917122223344"]

    style C fill:#e9c46a,color:#333
    style D fill:#f4a261,color:#333
    style E fill:#9b2226,color:#fff
```

---

## M05 Intent Classification Logic

```mermaid
flowchart TD
    A[Token List from M03] --> B[TF-IDF Vectorize\nUnigrams + Bigrams]
    B --> C[Logistic Regression\nPredict Proba]
    C --> D{Best class\nproba ≥ 0.4?}
    
    D -->|YES ✅| E[Return ML Intent\ne.g. 'placement', 'fee']
    D -->|NO 🔑| F[Keyword Fallback Map\n13 hand-crafted rules]
    F --> G{Any keyword\nmatches?}
    G -->|YES| H[Return Keyword Intent]
    G -->|NO| I[Return 'unknown']

    style E fill:#2d6a4f,color:#fff
    style H fill:#457b9d,color:#fff
    style I fill:#6c757d,color:#fff
```

---

## Data Flow Summary

```mermaid
flowchart LR
    subgraph DATA["📁 Data Files"]
        D1[data/faqs.json\n15 FAQs]
        D2[data/synonyms.json\nSynonym Dict]
        D3[data/intents.json\nML Training Examples]
        D4[analytics/logs.csv\nQuery History]
    end

    subgraph MODULES["🔧 Modules"]
        M1[M01 + M04\nUse faqs.json]
        M3[M03\nUses synonyms.json]
        M5[M05\nTrained on intents.json]
        M10[M10\nWrites to logs.csv]
    end

    D1 --> M1
    D2 --> M3
    D3 --> M5
    M10 --> D4
    D4 -->|GET /api/analytics| M09[M09 Analytics Tab]
```
