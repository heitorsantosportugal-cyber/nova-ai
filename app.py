
import streamlit as st

st.set_page_config(
    page_title="Nova AI",
    page_icon="✨",
    layout="wide"
)

st.markdown("""
<style>
.stApp {
    background: #0b1020;
    color: #f1f5f9;
}
[data-testid="stSidebar"] {
    background: #11182b;
}
.block-container {
    max-width: 1000px;
    padding-top: 3rem;
}
</style>
""", unsafe_allow_html=True)

if "messages" not in st.session_state:
    st.session_state.messages = []

if "conversations" not in st.session_state:
    st.session_state.conversations = []

with st.sidebar:
    st.title("✨ Nova AI")
    st.caption("O teu assistente inteligente")

    if st.button("＋ Nova conversa", use_container_width=True):
        if st.session_state.messages:
            st.session_state.conversations.append(
                st.session_state.messages.copy()
            )
        st.session_state.messages = []
        st.rerun()

    st.divider()
    st.subheader("Histórico")

    for i, conversation in enumerate(
        reversed(st.session_state.conversations)
    ):
        if st.button(
            f"Conversa {len(st.session_state.conversations) - i}",
            key=f"history_{i}",
            use_container_width=True
        ):
            st.session_state.messages = conversation.copy()
            st.rerun()

st.title("✨ Nova AI")
st.write("O teu espaço para aprender, criar e descobrir.")

st.markdown(
    "Olá! 👋 Sou a Nova AI. Em breve vou poder responder "
    "às tuas perguntas e analisar documentos."
)

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

prompt = st.chat_input("Escreve a tua mensagem...")

if prompt:
    st.session_state.messages.append({
        "role": "user",
        "content": prompt
    })

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        answer = (
            "Recebi a tua mensagem! 🚀 Ainda estou a ser construída. "
            "No próximo passo vamos ligar-me a um modelo de IA real."
        )
        st.markdown(answer)

    st.session_state.messages.append({
        "role": "assistant",
        "content": answer
    })
