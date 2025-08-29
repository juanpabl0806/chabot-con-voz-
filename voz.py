import os
import requests
import streamlit as st
from gtts import gTTS
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

API_URL = "https://api.deepseek.com/v1/chat/completions"

def get_secret(key, default=None):
    if st.secrets and key in st.secrets:
        return st.secrets[key]
    return os.environ.get(key, default)

API_KEY = get_secret("DEEPSEEK_API_KEY")
MODEL = get_secret("MODEL", "deepseek-chat")

SYSTEM_PROMPT = "Eres un tutor que solo explica qué son los sistemas digitales."

if not API_KEY:
    st.error("⚠️ Falta DEEPSEEK_API_KEY en secrets.")
    st.stop()

st.set_page_config(page_title="Chatbot con Voz", page_icon="🗣️")
st.title("🗣️ Chatbot: ¿Qué son los Sistemas Digitales?")

if "history" not in st.session_state:
    st.session_state.history = [{"role": "system", "content": SYSTEM_PROMPT}]

def chat_with_deepseek(prompt):
    messages = st.session_state.history + [{"role": "user", "content": prompt}]
    payload = {"model": MODEL, "messages": messages, "temperature": 0.3}
    headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
    try:
        r = requests.post(API_URL, headers=headers, json=payload, timeout=60)
        r.raise_for_status()
        data = r.json()
        return data["choices"][0]["message"]["content"]
    except Exception as e:
        return f"Error: {e}"

# Mostrar historial
for msg in st.session_state.history:
    if msg["role"] != "system":
        st.markdown(f"**{'Tú' if msg['role']=='user' else 'Bot'}:** {msg['content']}")

# Entrada de usuario (Enter para enviar)
user_input = st.chat_input("Escribe tu pregunta sobre sistemas digitales...")

if user_input:
    st.session_state.history.append({"role": "user", "content": user_input})
    response = chat_with_deepseek(user_input)
    st.session_state.history.append({"role": "assistant", "content": response})

    # Generar voz
    tts = gTTS(text=response, lang='es')
    tts.save("respuesta.mp3")
    st.audio("respuesta.mp3")

# Botón para reiniciar
if st.button("Reiniciar conversación"):
    st.session_state.history = [{"role": "system", "content": SYSTEM_PROMPT}]
    st.rerun()

