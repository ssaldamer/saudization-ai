import streamlit as st
import anthropic
import os
from dotenv import load_dotenv
from prompt import build_system_prompt

load_dotenv()

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Saudization AI Consultant",
    page_icon="🇸🇦",
    layout="centered"
)

# ── Header ─────────────────────────────────────────────────────────────────────
st.title("🇸🇦 Saudization AI Consultant")
st.caption("Ask about any sector or job to get data-driven recommendations for increasing Saudization rates.")

# ── Sidebar ─────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("About")
    st.write(
        "This tool analyzes real labor market and worker survey data "
        "to provide evidence-based Saudization recommendations."
    )
    st.divider()
    st.subheader("Example questions")
    examples = [
        "How can we increase Saudization in the IT sector?",
        "Which sector has the lowest Saudization rate and why?",
        "What does the survey data tell us about worker satisfaction in construction?",
        "Compare Saudization rates across all sectors",
        "What are the main barriers to hiring Saudi workers in retail?",
    ]
    for ex in examples:
        if st.button(ex, use_container_width=True):
            st.session_state.pending_question = ex

    st.divider()
    if st.button("🗑️ Clear conversation", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# ── Session state ───────────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []

if "system_prompt" not in st.session_state:
    with st.spinner("Loading data..."):
        st.session_state.system_prompt = build_system_prompt()

# ── Render chat history ─────────────────────────────────────────────────────────
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ── Handle sidebar example click ────────────────────────────────────────────────
if "pending_question" in st.session_state:
    user_input = st.session_state.pop("pending_question")
else:
    user_input = st.chat_input("Ask about any sector or job type...")

# ── Main chat logic ─────────────────────────────────────────────────────────────
if user_input:
    # Show user message
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # Call Claude API with streaming
    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        full_response = ""

        with client.messages.stream(
            model="claude-sonnet-4-20250514",
            max_tokens=1500,
            system=st.session_state.system_prompt,
            messages=[
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.messages
            ],
        ) as stream:
            for text in stream.text_stream:
                full_response += text
                response_placeholder.markdown(full_response + "▌")

        response_placeholder.markdown(full_response)

    st.session_state.messages.append({"role": "assistant", "content": full_response})
