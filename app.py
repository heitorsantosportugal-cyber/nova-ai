
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


# Inicializar o histórico
if "chats" not in st.session_state:
    st.session_state.chats = {
        "Conversa 1": []
    }

if "current_chat" not in st.session_state:
    st.session_state.current_chat = "Conversa 1"

if "document_text" not in st.session_state:
    st.session_state.document_text = ""

if "chat_counter" not in st.session_state:
    st.session_state.chat_counter = 1


def new_chat():
    st.session_state.chat_counter += 1
    name = f"Conversa {st.session_state.chat_counter}"

    st.session_state.chats[name] = []
    st.session_state.current_chat = name


# Barra lateral
with st.sidebar:
    st.title("✨ Nova AI")
    st.caption("O teu assistente inteligente")

    if st.button("＋ Nova conversa", use_container_width=True):
        new_chat()
        st.rerun()

    st.divider()
    st.subheader("💬 Histórico")

    for name in list(st.session_state.chats.keys()):
        col1, col2 = st.columns([4, 1])

        with col1:
            label = (
                "● " + name
                if name == st.session_state.current_chat
                else name
            )

            if st.button(
                label,
                key=f"open_{name}",
                use_container_width=True
            ):
                st.session_state.current_chat = name
                st.rerun()

        with col2:
            if st.button("🗑️", key=f"delete_{name}"):
                del st.session_state.chats[name]

                if not st.session_state.chats:
                    st.session_state.chat_counter += 1
                    new_name = (
                        f"Conversa {st.session_state.chat_counter}"
                    )
                    st.session_state.chats[new_name] = []

                if (
                    st.session_state.current_chat == name
                    or st.session_state.current_chat
                    not in st.session_state.chats
                ):
                    st.session_state.current_chat = next(
                        iter(st.session_state.chats)
                    )

                st.rerun()

    st.divider()
    st.subheader("📄 Documentos")

    uploaded_file = st.file_uploader(
        "Carrega um documento PDF",
        type=["pdf"],
        key="pdf_uploader"
    )

    if uploaded_file is not None:
        try:
            reader = PdfReader(
                BytesIO(uploaded_file.getvalue())
            )

            text = "\n".join(
                page.extract_text() or ""
                for page in reader.pages
            )

            st.session_state.document_text = text
            st.success("Documento carregado!")
            st.caption(
                f"{len(text):,} caracteres extraídos."
            )

        except Exception as error:
            st.error(f"Não foi possível ler o PDF: {error}")

    if st.session_state.document_text:
        if st.button("Remover texto do PDF"):
            st.session_state.document_text = ""
            st.rerun()


# Conversa selecionada
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
    - 🕘 Cria conversas e volta às anteriores pela barra lateral.
    """)

# Mostrar mensagens anteriores
for message in messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


# Campo de chat
prompt = st.chat_input(
    "Pergunta alguma coisa à Nova AI..."
)

if prompt:
    # Dar um título automático à primeira mensagem
    if not messages:
        title = prompt.strip().replace("\n", " ")[:32]

        if not title:
            title = "Nova conversa"

        original_title = title
        number = 2

        while (
            title in st.session_state.chats
            and title != st.session_state.current_chat
        ):
            title = f"{original_title[:27]} ({number})"
            number += 1

        old_name = st.session_state.current_chat

        if old_name != title:
            st.session_state.chats[title] = (
                st.session_state.chats.pop(old_name)
            )
            st.session_state.current_chat = title

        messages = st.session_state.chats[
            st.session_state.current_chat
        ]

    messages.append({
        "role": "user",
        "content": prompt
    })

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
                {
                    "role": "system",
                    "content": system_prompt
                }
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
                "Confirma a chave da API, os limites da conta e o modelo. "
                "Detalhes: " + str(error)
            )
            st.error(answer)

    messages.append({
        "role": "assistant",
        "content": answer
    })
