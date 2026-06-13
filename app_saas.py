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

if 'file_path' not in st.session_state:
    st.session_state.file_path = None

tab1, tab2 = st.tabs(["🔗 Pegar URL", "📁 Subir Video/Audio"])

with tab1:
    url_video = st.text_input("URL del video:")
    if st.button("Transcribir URL"):
        if url_video:
            with st.spinner("Conectando..."):
                try:
                    output_template = "/tmp/audio_final"
                    ydl_opts = {
                        'format': 'best',
                        'outtmpl': output_template,
                        'quiet': True,
                        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/126.0.0.0'
                    }
                    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                        ydl.download([url_video])
                    
                    possible_files = glob.glob(f"{output_template}*")
                    if possible_files: st.session_state.file_path = possible_files[0]
                except Exception as e: st.error(f"Error de descarga: {e}")
        else:
            st.warning("Por favor, ingresa una URL.")

with tab2:
    uploaded_file = st.file_uploader("Sube tu archivo (mp4, mp3, wav, webm):", type=['mp4', 'mp3', 'wav', 'webm'])
    
    if uploaded_file is not None:
        if st.button("Procesar Archivo Subido"):
            path = f"/tmp/{uploaded_file.name}"
            with open(path, "wb") as f: f.write(uploaded_file.getbuffer())
            st.session_state.file_path = path

# Proceso de transcripción unificado
if st.session_state.file_path:
    try:
        with st.spinner("La IA está transcribiendo..."):
            model = whisper.load_model("base")
            resultado = model.transcribe(st.session_state.file_path)
            st.success("¡Transcripción lista!")
            st.text_area("Resultado:", resultado["text"], height=300)
        
        # Limpieza después de procesar
        if os.path.exists(st.session_state.file_path): 
            os.remove(st.session_state.file_path)
        st.session_state.file_path = None
    except Exception as e:
        st.error(f"Error en IA: {e}")
        st.session_state.file_path = None
