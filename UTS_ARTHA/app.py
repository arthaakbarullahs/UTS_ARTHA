# ================================================================
# Chatbot Gemini — Open Chat + Kemampuan Prediksi Mobil Upgrade!
# ================================================================

import os
import streamlit as st
import google.generativeai as genai
from PIL import Image

# ---------------------- Konfigurasi ----------------------------
st.set_page_config(page_title="Gemini Smart Chat", page_icon="🚙", layout="wide")

# Custom CSS UI
st.markdown("""
<style>
    .chat-bubble-user {
        background-color: #999;
        border-radius: 10px;
        padding: 10px;
        margin: 5px 0;
    }
    .chat-bubble-bot {
        background-color: #666;
        border-radius: 10px;
        padding: 10px;
        margin: 5px 0;
    }
    .sidebar .sidebar-content {
        background-color: #1F2937;
    }
</style>
""", unsafe_allow_html=True)

st.title("🤖 Gemini Smart AutoChat 🚗")

# Pastikan API Key di environment variable
API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
if not API_KEY:
    st.error("""
    ❌ API Key belum diset.
    Jalankan perintah ini di PowerShell sebelum membuka Streamlit:

    $env:GEMINI_API_KEY="AIzaSyDtERmcTO-q-PiVYmgJ5KFhHv1qbgzlMX0"
    """)
    st.stop()

genai.configure(api_key=API_KEY)


# Sidebar UI
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/5/51/Google_Gemini_logo.svg/512px-Google_Gemini_logo.svg.png ",width=160)
    st.subheader("⚙️ Pengaturan Chat")
    GMODEL_NAME = st.selectbox(
        "Pilih Model",
        ["models/gemini-2.0-flash", "models/gemini-1.5-flash", "models/gemini-1.5-pro"]
    )
    if st.button("🔄 Reset Chat"):
        st.session_state.messages = []
        st.session_state.user_budget = None
        st.rerun()

GMODEL = genai.GenerativeModel(GMODEL_NAME)
# ---------------------- Memory / History -----------------------
if "chat_history" not in st.session_state:
    st.session_state.chat_history = {}  # {nama_history: messages[]}

if "archived_history" not in st.session_state:
    st.session_state.archived_history = {}

with st.sidebar:
    st.subheader("📜 Riwayat Chat")

    # Pilih history jika ada
    history_list = list(st.session_state.chat_history.keys())
    selected_history = st.selectbox(
        "History",
        ["-- Tidak ada --"] + history_list
    )

    if selected_history != "-- Tidak ada --":
        if st.button("📦 Arsipkan"):
            st.session_state.archived_history[selected_history] = st.session_state.chat_history.pop(selected_history)
            st.success("Berhasil diarsipkan!")
            st.rerun()

        if st.button("🗑️ Hapus"):
            st.session_state.chat_history.pop(selected_history)
            st.warning("History dihapus!")
            st.rerun()

        if st.button("🔄 Load Chat"):
            st.session_state.messages = st.session_state.chat_history[selected_history].copy()
            st.success("History dimuat!")
            st.rerun()

    st.divider()
    st.subheader("🔄 Reset Chat")
    if st.button("Reset Sekarang"):
        # Simpan dulu chat lama jadi history baru
        if len(st.session_state.messages) > 1:
            name = f"Chat {len(st.session_state.chat_history) + 1}"
            st.session_state.chat_history[name] = st.session_state.messages.copy()
        st.session_state.messages = []
        st.session_state.user_budget = None
        st.rerun()


# ---------------------- State Chat -----------------------------
if "messages" not in st.session_state:
    st.session_state.messages = [{
        "role": "assistant",
        "content": "Halo! Aku Gemini 🚗💡 Siap bantu kamu dalam apa pun ✨"
    }]
    st.session_state.user_budget = None

# Display chat messages with prettier bubbles
for msg in st.session_state.messages:
    role = msg["role"]
    style = "chat-bubble-bot" if role == "assistant" else "chat-bubble-user"
    with st.chat_message(role):
        st.markdown(f"<div class='{style}'>{msg['content']}</div>", unsafe_allow_html=True)

# Input User
user_input = st.chat_input("Ketik sesuatu...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})

    with st.chat_message("user"):
        st.markdown(f"<div class='chat-bubble-user'>{user_input}</div>", unsafe_allow_html=True)

    # Build context
    context = "\n".join(
        [f"{m['role']}: {m['content']}" for m in st.session_state.messages[-10:]]
    )

    prompt = f"""
    Kamu adalah Gemini yang ramah dan santai.
    {context}
    Jawab pesan user dengan gaya natural dan menyenangkan.
    """

    response = GMODEL.generate_content(prompt)
    answer = response.text.strip() if response and response.text else "Ups, bisa ulangi? 😅"

    with st.chat_message("assistant"):
        st.markdown(f"<div class='chat-bubble-bot'>{answer}</div>", unsafe_allow_html=True)

    st.session_state.messages.append({"role": "assistant", "content": answer})