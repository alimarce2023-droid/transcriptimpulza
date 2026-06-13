import streamlit as st
import yt_dlp
import whisper
import os
import glob
from googletrans import Translator

# Configuración
st.set_page_config(page_title="ProTranscribe - Impulza Digital", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #0d0d0d; color: #ffffff; }
    h1 { color: #FFCC00 !important; text-transform: uppercase; font-weight: 800; }
    .stTextInput label { color: #FFCC00 !important; font-weight: bold !important; }
    .stButton>button { 
        background-color: #FFCC00 !important; color: #000000 !important; font-weight: 800 !important; 
        border-radius: 10px !important; border: 2px solid #84139B !important; 
    }
    </style>
""", unsafe_allow_html=True)

st.title("ProTranscribe - Impulza Digital")

# Limpieza inicial
for f in glob.glob("/tmp/audio_*"):
    try: os.remove(f)
    except: pass

# MANTENEMOS ESTA ESTRUCTURA DE TABS EN EL NIVEL SUPERIOR
tab1, tab2 = st.tabs(["🔗 Pegar URL", "📁 Subir Video/Audio"])

file_path = None

with tab1:
    url_video = st.text_input("URL del video:")
    if st.button("Procesar URL"):
        with st.spinner("Descargando..."):
            try:
                ydl_opts = {'format': 'best', 'outtmpl': '/tmp/audio_final', 'quiet': True}
                with yt_dlp.YoutubeDL(ydl_opts) as ydl: ydl.download([url_video])
                possible = glob.glob("/tmp/audio_final*")
                if possible: file_path = possible[0]
            except Exception as e: st.error(f"Error: {e}")

with tab2:
    uploaded_file = st.file_uploader("Sube tu archivo:", type=['mp4', 'mp3', 'wav'])
    if uploaded_file and st.button("Procesar Archivo"):
        file_path = f"/tmp/{uploaded_file.name}"
        with open(file_path, "wb") as f: f.write(uploaded_file.getbuffer())

# TRANSCRIPCIÓN Y TRADUCCIÓN
if file_path:
    with st.spinner("IA transcribiendo..."):
        model = whisper.load_model("base")
        res = model.transcribe(file_path)
        texto_original = res["text"]
        st.success("¡Transcripción lista!")
        st.text_area("Original:", texto_original, height=150)
        
        # Selector de idioma
        idiomas = {"Español": "es", "Inglés": "en", "Francés": "fr", "Italiano": "it", "Portugués": "pt"}
        target = st.selectbox("Traducir a:", list(idiomas.keys()))
        
        if st.button("Traducir"):
            try:
                translator = Translator()
                traduccion = translator.translate(texto_original, dest=idiomas[target])
                st.text_area("Resultado traducido:", traduccion.text, height=150)
            except Exception as e:
                st.error(f"Error en traducción: {e}")

    if os.path.exists(file_path): os.remove(file_path)
