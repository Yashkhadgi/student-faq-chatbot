# M-09: Streamlit Chat UI + Analytics Dashboard
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import pandas as pd
from modules.m02_preprocessor      import preprocess
from modules.m03_synonym_expander   import expand_synonyms
from modules.m04_tfidf_retrieval    import retrieve
from modules.m05_intent_classifier  import classify_intent
from modules.m06_entity_extractor   import extract_entities
from modules.m07_context_manager    import update_context, enrich_with_context
from modules.m08_fallback_handler   import handle_fallback
from analytics.m10_analytics_logger import log_event, get_analytics_summary, get_recent_logs
from config                         import CONFIDENCE_THRESHOLD

def process_query(raw_query: str, session: dict) -> dict:
    tokens          = preprocess(raw_query)
    enriched        = enrich_with_context(raw_query, tokens, session)
    expanded_tokens = expand_synonyms(enriched["tokens"])
    intent          = classify_intent(enriched["tokens"])
    entities        = extract_entities(raw_query)
    results         = retrieve(expanded_tokens)

    if results and results[0]["score"] >= CONFIDENCE_THRESHOLD:
        answer = results[0]["answer"]
        status = "answered"
    else:
        answer = handle_fallback(raw_query, results)
        status = "fallback"

    update_context(session, raw_query, answer, intent, entities)
    log_event(raw_query, intent, entities, results[0]["score"] if results else 0, status)

    return {
        "answer":      answer,
        "intent":      intent,
        "status":      status,
        "top_matches": results
    }

st.set_page_config(page_title="SIT EduBot", page_icon="🎓", layout="wide")

st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Chat", "Analytics Dashboard"])

if page == "Chat":
    st.sidebar.markdown("---")
    st.sidebar.subheader("Multichannel Simulator")
    channel_mode = st.sidebar.radio("View as:", ["Web Chat", "Mobile App (simulated)", "WhatsApp (simulated)"])

    st.title("🎓 Student FAQ Chatbot")
    
    # Simple formatting based on channel selected
    if channel_mode == "WhatsApp (simulated)":
        st.markdown(
            "<style>.stChatMessage { background-color: #e5ddd5 !important; border-radius: 12px; color: black; } </style>", 
            unsafe_allow_html=True
        )
        st.caption("You are viewing the WhatsApp simulated experience.")
        prefix = "🤖 EduBot: "
    elif channel_mode == "Mobile App (simulated)":
        st.markdown(
            "<style>.stChatMessage { box-shadow: 0 4px 8px 0 rgba(0,0,0,0.2) !important; border-radius: 15px; } </style>", 
            unsafe_allow_html=True
        )
        st.caption("You are viewing the Mobile App simulated experience.")
        prefix = "📱 "
    else:
        st.caption("Ask me anything about admissions, fees, exams, schedules & more!")
        prefix = ""

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "session" not in st.session_state:
        st.session_state.session = {"history": []}

    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if prompt := st.chat_input("Type your question here..."):
        with st.chat_message("user"):
            st.markdown(prompt)
        st.session_state.chat_history.append({"role": "user", "content": prompt})

        with st.spinner("Thinking..."):
            response = process_query(prompt, st.session_state.session)

        with st.chat_message("assistant"):
            final_ans = prefix + response["answer"]
            st.markdown(final_ans)
            st.caption(f"Intent: `{response['intent']}` | Status: `{response['status']}`")

        st.session_state.chat_history.append({
            "role":    "assistant",
            "content": final_ans
        })

elif page == "Analytics Dashboard":
    st.title("📊 Chatbot Analytics Dashboard")
    st.caption("Monitor chatbot performance, view fallback rates, and identify missing FAQs.")
    
    stats = get_analytics_summary()
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Queries", stats["total_queries"])
    col2.metric("Fallback Rate", f"{stats['fallback_rate']}%")
    col3.metric("Avg Confidence", stats["avg_confidence"])
    
    st.subheader("Intent Distribution")
    if stats["intent_distribution"]:
        st.bar_chart(pd.DataFrame.from_dict(stats["intent_distribution"], orient='index', columns=['Count']))
    else:
        st.info("No data available yet.")
        
    st.subheader("Recent Interactions")
    logs = get_recent_logs(50)
    if logs:
        st.dataframe(pd.DataFrame(logs)[["timestamp", "query", "intent", "score", "response"]])
    else:
        st.info("No interactions found.")
        
    st.subheader("Suggested Improvements")
    st.markdown("Users asked these questions, but the bot didn't have a confident answer. Consider adding them to `faqs.json`.")
    unanswered = list(set([log["query"] for log in logs if log["response"] == "fallback"]))
    if unanswered:
        for q in unanswered:
            st.markdown(f"- {q}")
    else:
        st.success("No fallbacks detected recently! The bot is doing great.")
