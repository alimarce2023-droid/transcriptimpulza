import streamlit as st
import yt_dlp
import whisper
import os
import glob
import random
from deep_translator import GoogleTranslator

# Configuración de página
st.set_page_config(page_title="ProTranscribe AI", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #0d0d0d; color: #ffffff; }
    h1 { color: #FFCC00 !important; text-transform: uppercase; font-weight: 800; }
    .stButton>button { background-color: #FFCC00 !important; color: #000000 !important; font-weight: 800 !important; border-radius: 10px !important; }
    .stTextInput label { color: #FFCC00 !important; font-weight: bold !important; }
    </style>
""", unsafe_allow_html=True)

st.title("🌐 ProTranscribe - Impulza Digital")

tab1, tab2 = st.tabs(["🔗 URL", "📁 Subir Archivo"])
file_path = None

with tab1:
    url = st.text_input("URL del video:")
    if st.button("Procesar URL"):
        with st.spinner("Descargando..."):
            try:
                for f in glob.glob("/tmp/audio_*"): os.remove(f)
                
                ydl_opts = {
                    'format': 'best',
                    'outtmpl': '/tmp/audio_final',
                    'quiet': True,
                    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36'
                }
                with yt_dlp.YoutubeDL(ydl_opts) as ydl: ydl.download([url])
                
                files = glob.glob("/tmp/audio_final*")
                if files: file_path = files[0]
            except Exception as e: st.error(f"Error: {e}")

with tab2:
    archivo = st.file_uploader("Sube tu archivo (mp4, mp3, wav):", type=['mp4', 'mp3', 'wav'])
    if archivo:
        file_path = f"/tmp/{archivo.name}"
        with open(file_path, "wb") as f: f.write(archivo.getbuffer())

# Motor de transcripción y traducción
if file_path:
    with st.spinner("Procesando audio..."):
        try:
            model = whisper.load_model("base")
            res = model.transcribe(file_path)
            texto_base = res["text"]
            
            st.success("¡Transcripción lista!")
            st.text_area("Transcripción Original:", texto_base, height=200)
            
            # Traducción usando deep-translator
            idioma = st.selectbox("¿Quieres traducirlo?", ["Ninguno", "Inglés", "Francés", "Italiano", "Portugués"])
            if idioma != "Ninguno":
                mapa = {"Inglés": "en", "Francés": "fr", "Italiano": "it", "Portugués": "pt"}
                traducido = GoogleTranslator(source='auto', target=mapa[idioma]).translate(texto_base)
                st.text_area(f"Traducción a {idioma}:", traducido, height=200)
            
            if os.path.exists(file_path): os.remove(file_path)
        except Exception as e:
            st.error(f"Error IA: {e}")
