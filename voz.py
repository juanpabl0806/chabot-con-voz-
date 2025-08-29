import os
import requests
import streamlit as st
from gtts import gTTS

# ===== CONFIGURACIÓN =====
API_URL = "https://api.deepseek.com/v1/chat/completions"
API_KEY = st.secrets["DEEPSEEK_API_KEY"]
MODEL = "deepseek-chat"
SYSTEM_PROMPT = """
Eres un asistente que responde únicamente sobre qué son los sistemas digitales,
sus características, ejemplos y aplicaciones. Responde en español de manera breve y clara.
Si la pregunta no está relacionada, responde: "Solo puedo responder sobre sistemas digitales."
"""

# ===== FUNCIÓN DE TEXTO A VOZ =====
def speak_text(text):
    try:
        output_path = "audio_response.mp3"
        tts = gTTS(text, lang="es")
        tts.save(output_path)
        return output_path
    except Exception as e:
        st.error(f"Error al generar audio: {e}")
        return None

# ===== INTERFAZ =====
st.set_page_config(page_title="Chatbot Sistemas Digitales", page_icon="🤖")
st.title("🤖 Chatbot sobre Sistemas Digitales")

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
    if msg["role"] == "system":
        continue
    st.markdown(f"**{'Tú' if msg['role']=='user' else 'Bot'}:** {msg['content']}")

# Entrada del usuario
user_input = st.chat_input("Pregunta sobre sistemas digitales...")
if user_input:
    st.session_state.history.append({"role": "user", "content": user_input})
    response = chat_with_deepseek(user_input)
    st.session_state.history.append({"role": "assistant", "content": response})

    # Reproducir respuesta en audio
    audio_file = speak_text(response)
    if audio_file:
        st.audio(audio_file, format="audio/mp3")

    st.rerun()

# Botón para reiniciar conversación
if st.button("Reiniciar conversación"):
    st.session_state.history = [{"role": "system", "content": SYSTEM_PROMPT}]
    st.rerun()
