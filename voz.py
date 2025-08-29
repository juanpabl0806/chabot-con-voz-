import os
import requests
import streamlit as st
from gtts import gTTS
from dotenv import load_dotenv

# === CARGAR VARIABLES DE ENTORNO ===
load_dotenv()

API_URL = "https://api.deepseek.com/v1/chat/completions"

def get_secret(key, default=None):
    if st.secrets and key in st.secrets:
        return st.secrets[key]
    return os.environ.get(key, default)

API_KEY = get_secret("DEEPSEEK_API_KEY")
MODEL = "deepseek-chat"
SYSTEM_PROMPT = "Responde solo sobre qué son los sistemas digitales."

if not API_KEY:
    st.error("⚠️ No se encontró la clave DEEPSEEK_API_KEY. Configúrala en Streamlit Secrets.")
    st.stop()

# === CONFIGURACIÓN DE INTERFAZ ===
st.set_page_config(page_title="Chatbot con Voz", page_icon="🎙️")
st.title("🤖 Chatbot sobre Sistemas Digitales con Voz")

if "history" not in st.session_state:
    st.session_state.history = [{"role": "system", "content": SYSTEM_PROMPT}]

# === FUNCIONES ===
def chat_with_deepseek(prompt):
    messages = st.session_state.history + [{"role": "user", "content": prompt}]
    payload = {"model": MODEL, "messages": messages, "temperature": 0.3}
    headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
    try:
        r = requests.post(API_URL, headers=headers, json=payload, timeout=60)
        r.raise_for_status()
        data = r.json()
        response = data["choices"][0]["message"]["content"]
        return response
    except Exception as e:
        return f"Error: {e}"

def speak_text(text):
    try:
        st.write("Texto enviado a gTTS:", text)  # Depuración
        tts = gTTS(text, lang="es")
        output_path = "audio_response.mp3"
        tts.save(output_path)
        return output_path
    except Exception as e:
        st.error(f"Error en gTTS: {e}")
        return None

# === MOSTRAR HISTORIAL ===
for msg in st.session_state.history:
    if msg["role"] == "system":
        continue
    st.markdown(f"**{'Tú' if msg['role']=='user' else 'Bot'}:** {msg['content']}")

# === ENTRADA DEL USUARIO ===
user_input = st.text_input("Escribe tu pregunta:", key="input")
if st.button("Enviar") and user_input:
    st.session_state.history.append({"role": "user", "content": user_input})
    response = chat_with_deepseek(user_input)
    st.session_state.history.append({"role": "assistant", "content": response})

    # Mostrar texto
    st.markdown(f"**Bot:** {response}")

    # Generar audio
    audio_file = speak_text(response)
    if audio_file:
        st.audio(audio_file)

# === BOTÓN DE REINICIO ===
if st.button("Reiniciar conversación"):
    st.session_state.history = [{"role": "system", "content": SYSTEM_PROMPT}]
    st.rerun()

