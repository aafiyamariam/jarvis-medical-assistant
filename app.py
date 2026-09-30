import streamlit as st

from src.rag import answer, cited_sources

st.set_page_config(page_title="Jarvis - Medical Information Assistant", page_icon="🩺")
st.title("🩺 Jarvis")
st.caption(
    "General health information from MedlinePlus (NIH). Not medical advice. "
    "In an emergency, call your local emergency number."
)

if "messages" not in st.session_state:
    st.session_state.messages = []

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

question = st.chat_input("Ask a health question...")
if question:
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        with st.spinner("Searching medical documents..."):
            text, hits = answer(question)
        sources = cited_sources(text, hits)
        if sources:
            lines = []
            for name, url in sources:
                label = name.replace("medlineplus_", "").replace("_", " ").title()
                lines.append(f"- [{label} (MedlinePlus)]({url})")
            text += "\n\n**Sources:**\n" + "\n".join(lines)
        st.markdown(text)

    st.session_state.messages.append({"role": "assistant", "content": text})