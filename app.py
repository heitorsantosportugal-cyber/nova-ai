

import streamlit as st
from groq import Groq
from pypdf import PdfReader
from io import BytesIO

st.set_page_config(
    page_title="Nova AI",
    page_icon="✨",
    layout="wide"
)

st.markdown("""
<style>
.stApp {
    background: #0b1020;
    color: #eef2ff;
}
[data-testid="stSidebar"] {
    background: #11182b;
}
.block-container {
    max-width: 950px;
    padding-top: 2.5rem;
}
[data-testid="stChatMessage"] {
    border: 1px solid #28334d;
    border-radius: 16px;
    padding: 12px;
}
.stChatInput textarea {
    background: #11182b;
}
</style>
""", unsafe_allow_html=True)

if "chats" not in st.session_state:
    st.session_state.chats = {"Nova conversa": []}

if "current_chat" not in st.session_state:
    st.session_state.current_chat = "Nova conversa"

if "document_text" not in st.session_state:
    st.session_state.document_text = ""

def new_chat():
    name = f"Conversa {len(st.session_state.chats) + 1}"
    st.session_state.chats[name] = []
    st.session_state.current_chat = name

with st.sidebar:
    st.title("✨ Nova AI")
    st.caption("O teu assistente inteligente")

    if st.button("＋ Nova conversa", use_container_width=True):
        new_chat()
        st.rerun()

    st.divider()
    st.subheader("Histórico")

    for name in list(st.session_state.chats.keys()):
        if st.button(name, key=f"chat_{name}",
                      use_container_width=True):
            st.session_state.current_chat = name
            st.rerun()

    st.divider()
    st.subheader("📄 Documentos")

    uploaded_file = st.file_uploader(
        "Carrega um documento PDF",
        type=["pdf"]
    )

    if uploaded_file is not None:
        try:
            reader = PdfReader(BytesIO(uploaded_file.getvalue()))
            text = "\n".join(
                page.extract_text() or ""
                for page in reader.pages
            )
            st.session_state.document_text = text
            st.success("Documento carregado!")
            st.caption(f"{len(text):,} caracteres extraídos.")
        except Exception as error:
            st.error(f"Não foi possível ler o PDF: {error}")

messages = st.session_state.chats[
    st.session_state.current_chat
]

st.title("✨ Nova AI")
st.caption("Aprende, cria e descobre — tudo numa conversa.")

if not messages:
    st.markdown("""
    ### Olá! 👋 Sou a Nova AI.

    Estou aqui para te ajudar.

    - 💬 Faz perguntas sobre qualquer tema.
    - 📚 Aprende coisas novas.
    - 📄 Carrega um PDF e pergunta-me sobre o documento.
    """)

for message in messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

prompt = st.chat_input("Pergunta alguma coisa à Nova AI...")

if prompt:
    messages.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            api_key = st.secrets["GROQ_API_KEY"]
            client = Groq(api_key=api_key)

            system_prompt = (
                "És a Nova AI, um assistente útil, claro e simpático. "
                "Responde na língua do utilizador. "
                "Se receberes texto de um documento, responde com base "
                "nele quando a pergunta estiver relacionada."
            )

            if st.session_state.document_text:
                system_prompt += (
                    "\n\nTexto do documento enviado pelo utilizador:\n"
                    + st.session_state.document_text[:20000]
                )

            api_messages = [
                {"role": "system", "content": system_prompt}
            ]

            api_messages.extend(messages[-20:])

            response = client.chat.completions.create(
               model="openai/gpt-oss-120b",
                messages=api_messages,
                temperature=0.7,
                max_tokens=1500
            )

            answer = response.choices[0].message.content
            st.markdown(answer)

        except Exception as error:
            answer = (
                "Não consegui obter uma resposta da IA. "
                "Confirma a chave da API, os limites da conta e o modelo "
                "configurado. Detalhes: " + str(error)
            )
            st.error(answer)

    messages.append({
        "role": "assistant",
        "content": answer
    })
