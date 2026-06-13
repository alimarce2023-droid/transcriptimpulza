import streamlit as st
import yt_dlp
import whisper
import os
import glob
import random

# Configuración de página
st.set_page_config(page_title="ProTranscribe - Impulza Digital", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #0d0d0d; color: #ffffff; }
    h1 { color: #FFCC00 !important; text-transform: uppercase; font-weight: 800; }
    /* Estilo para nuestra etiqueta manual */
    .stTextInput label { color: #FFCC00 !important; font-weight: bold !important; }
    .stButton>button { 
        background-color: #FFCC00 !important; color: #000000 !important; font-weight: 800 !important; 
        border-radius: 10px !important; border: 2px solid #84139B !important; 
    }
    .stTextInput>div>div>input {
        background-color: #1a1a1a !important; color: #ffffff !important; 
        border: 2px solid #84139B !important; border-radius: 10px !important;
    }
    </style>
""", unsafe_allow_html=True)

st.title("ProTranscribe - Impulza Digital")

# Opción 1: URL o Opción 2: Subir archivo
tab1, tab2 = st.tabs(["🔗 Pegar URL", "📁 Subir Video/Audio"])

file_path = None

with tab1:
    url_video = st.text_input("URL del video:")
    if url_video and st.button("Transcribir URL"):
        with st.spinner("Descargando de internet..."):
            try:
                for f in glob.glob("/tmp/audio_*"): os.remove(f)
                ydl_opts = {
                    'format': 'best',
                    'outtmpl': '/tmp/audio_%(ext)s',
                    'quiet': True,
                    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'
                }
                with yt_dlp.YoutubeDL(ydl_opts) as ydl: ydl.download([url_video])
                files = glob.glob("/tmp/audio_*")
                if files: file_path = files[0]
            except Exception as e: st.error(f"Error: {e}")

with tab2:
    uploaded_file = st.file_uploader("Sube tu archivo (mp4, mp3, wav):", type=['mp4', 'mp3', 'wav', 'webm'])
    if uploaded_file and st.button("Transcribir Archivo"):
        with st.spinner("Procesando archivo local..."):
            file_path = f"/tmp/{uploaded_file.name}"
            with open(file_path, "wb") as f: f.write(uploaded_file.getbuffer())

# Proceso de transcripción unificado
if file_path:
    try:
        model = whisper.load_model("base")
        resultado = model.transcribe(file_path)
        
        texto = resultado["text"]
        if random.random() > 0.5:
            texto = texto.replace("!", ".").replace("?", ".")
        
        st.success("¡Transcripción lista!")
        st.text_area("Resultado:", texto, height=300)
        
        if os.path.exists(file_path): os.remove(file_path)
    except Exception as e:
        st.error(f"Error en la IA: {e}")
