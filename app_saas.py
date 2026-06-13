import streamlit as st
import yt_dlp
import whisper
import os
import glob
from deep_translator import GoogleTranslator

# Configuración de página
st.set_page_config(page_title="ProTranscribe AI", layout="wide")

st.title("🌐 ProTranscribe - Impulza Digital")

# Inicialización de estado
if 'texto_transcrito' not in st.session_state:
    st.session_state.texto_transcrito = None

# Función para dividir texto largo y traducir por partes
def traducir_texto_largo(texto, destino):
    # Dividimos en trozos de 4000 caracteres para estar seguros bajo el límite de 5000
    limite = 4000
    trozos = [texto[i:i+limite] for i in range(0, len(texto), limite)]
    traductor = GoogleTranslator(source='auto', target=destino)
    traducciones = [traductor.translate(t) for t in trozos]
    return " ".join(traducciones)

tab1, tab2 = st.tabs(["🔗 URL", "📁 Subir Archivo"])

# Pestaña 1: URL
with tab1:
    url = st.text_input("URL del video:")
    if st.button("Procesar URL"):
        with st.spinner("Descargando..."):
            try:
                # Limpieza previa
                for f in glob.glob("/tmp/audio_final*"): os.remove(f)
                
                ydl_opts = {
                    'format': 'bestaudio/best',
                    'outtmpl': '/tmp/audio_final',
                    'quiet': True
                }
                with yt_dlp.YoutubeDL(ydl_opts) as ydl: ydl.download([url])
                
                # Buscar archivo descargado
                files = glob.glob("/tmp/audio_final*")
                if files:
                    model = whisper.load_model("base")
                    res = model.transcribe(files[0])
                    st.session_state.texto_transcrito = res["text"]
                    os.remove(files[0])
            except Exception as e: st.error(f"Error: {e}")

# Pestaña 2: Subida
with tab2:
    archivo = st.file_uploader("Sube tu archivo (mp4, mp3, wav):", type=['mp4', 'mp3', 'wav'])
    if archivo is not None:
        if st.button("Transcribir archivo subido"):
            with st.spinner("Procesando..."):
                path = f"/tmp/{archivo.name}"
                with open(path, "wb") as f: f.write(archivo.getbuffer())
                
                model = whisper.load_model("base")
                res = model.transcribe(path)
                st.session_state.texto_transcrito = res["text"]
                os.remove(path)

# Visualización y Traducción
if st.session_state.texto_transcrito:
    st.success("¡Transcripción lista!")
    st.text_area("Transcripción Original:", st.session_state.texto_transcrito, height=200)
    
    idioma = st.selectbox("¿Quieres traducirlo?", ["Ninguno", "Español", "Inglés", "Francés", "Italiano", "Portugués"])
    
    if idioma != "Ninguno":
        mapa = {"Español": "es", "Inglés": "en", "Francés": "fr", "Italiano": "it", "Portugués": "pt"}
        with st.spinner("Traduciendo (esto puede tomar un momento)..."):
            try:
                traducido = traducir_texto_largo(st.session_state.texto_transcrito, mapa[idioma])
                st.text_area(f"Traducción a {idioma}:", traducido, height=200)
            except Exception as e:
                st.error(f"Error en la traducción: {e}")
