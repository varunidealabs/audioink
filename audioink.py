import streamlit as st
import requests
import os
from io import BytesIO
from pydub import AudioSegment
from pydub.utils import which

# Set FFmpeg paths automatically
AudioSegment.converter = which("ffmpeg")
AudioSegment.ffmpeg = which("ffmpeg")
AudioSegment.ffprobe = which("ffprobe")

# Page Config
st.set_page_config(page_title="AudioInk", page_icon="🎙️", layout="wide")

# Custom CSS Styling
st.markdown(
    """
    <style>
        .stApp { background-color: #000000; color: #FF5C0A; font-family: 'Times New Roman'; }
        .sidebar .sidebar-content { background-color: #ffffff; }
        .stButton button { border-radius: 8px; background-color: #007BFF; color: white; }
        .stTabs [data-baseweb="tab-list"] { justify-content: start; }
        .sidebar-title { color: #FF5C0A; font-size: 24px; font-weight: bold; }
        .top-right-image { position: absolute; top: 8px; right: 8px; }
    </style>
    """,
    unsafe_allow_html=True
)

# API Configuration
AZURE_WHISPER_API_URL = "https://your-api-endpoint.azure.com"
API_KEY = "your_api_key_here"
SUPPORTED_FORMATS = ["mp3", "mp4", "mpeg", "mpga", "m4a", "wav", "webm"]
MAX_FILE_SIZE = 25 * 1024 * 1024

# Transcription Function
def transcribe_audio(audio_file):
    headers = {"api-key": API_KEY, "Authorization": f"Bearer {API_KEY}"}
    try:
        with st.spinner("Transcribing audio..."):
            audio_file.seek(0)
            files = {"file": (audio_file.name, audio_file, "audio/wav")}
            response = requests.post(AZURE_WHISPER_API_URL, headers=headers, files=files, timeout=60)
            if response.status_code == 200:
                return True, response.json().get("text", "No text returned from API")
            return False, f"API Error: {response.status_code} - {response.text}"
    except requests.exceptions.RequestException as e:
        return False, f"Error: {str(e)}"

# Validate Uploaded File
def validate_file(file):
    if not file:
        return False, "No file uploaded."
    if file.size > MAX_FILE_SIZE:
        return False, "File too large. Max size is 25MB."
    if file.name.split(".")[-1].lower() not in SUPPORTED_FORMATS:
        return False, "Unsupported file format."
    return True, "File is valid."

# Convert Audio to WAV
def convert_to_wav(audio_file):
    try:
        file_extension = audio_file.name.split(".")[-1].lower()
        if file_extension == "wav":
            return audio_file
        audio_bytes = audio_file.read()
        audio_file.seek(0)
        audio = AudioSegment.from_file(BytesIO(audio_bytes), format=file_extension)
        wav_io = BytesIO()
        audio.export(wav_io, format="wav")
        wav_io.seek(0)
        wav_io.name = f"{os.path.splitext(audio_file.name)[0]}.wav"
        return wav_io
    except Exception as e:
        st.error(f"Error converting audio: {str(e)}")
        return None

# Sidebar Layout
st.sidebar.image("mic.png", width=100)
st.sidebar.markdown("<div class='sidebar-title'>🎙️ AudioInk</div>", unsafe_allow_html=True)

page = st.sidebar.radio("Navigation", ["Home", "Upload Audio", "Record Audio", "About"], index=0)


if page=="Home":
    # Custom CSS
    st.markdown("""
    <style>
        /* Reset default Streamlit styling */
        .stApp {
            background-color: #f8f8fb;
            font-family: 'Inter', 'Helvetica Neue', sans-serif;
        }
        
        /* Main Container Styling */
        .main-container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 2rem;
            text-align: center;
        }
        
        /* Hero Title Styling */
        .hero-title {
            font-size: 4.5rem;
            font-weight: 800;
            color: #2c3e50;
            line-height: 1.2;
            margin-bottom: 1rem;
        }
        
        /* Highlight Word Styling */
        .highlight {
            color: #ff5722;
        }
        
        /* Subtitle Styling */
        .subtitle {
            font-size: 1.5rem;
            color: #637082;
            max-width: 700px;
            margin: 0 auto 2rem;
        }
        
        /* Button Styling */
        .cta-buttons {
            display: flex;
            justify-content: center;
            gap: 1rem;
            margin-top: 2rem;
        }
        .cta-buttons a {
            text-decoration: none;
            padding: 12px 24px;
            border-radius: 50px;
            font-weight: 600;
            transition: all 0.3s ease;
        }
        .primary-button {
            background-color: #ff5722;
            color: white !important;
        }
        .secondary-button {
            background-color: #f0f0f5;
            color: #2c3e50 !important;
        }
        
        /* Microphone Icon Styling */
        .microphone-icon {
            font-size: 5rem;
            color: #ff5722;
            margin-top: 2rem;
        }
    </style>
    """, unsafe_allow_html=True)

    # Main Container
    st.markdown('<div class="main-container">', unsafe_allow_html=True)
    
    # Hero Title
    st.markdown('''
    <h1 class="hero-title">
        Go from <span class="highlight">fuzzy thought</span><br>
        to clear text. <span class="highlight">Fast.</span>
    </h1>
    ''', unsafe_allow_html=True)
    
    # Subtitle
    st.markdown('''
    <p class="subtitle">
    AudioScribe converts voice notes into text that's easy to read and ready to share.
    Create meeting notes, memos, emails, articles and more. 
    All you have to do is talk.
    </p>
    ''', unsafe_allow_html=True)
    
    # CTA Buttons
    st.markdown('''
    <div class="cta-buttons">
        <a href="#" class="cta-buttons a primary-button">Start Transcribing</a>
        <a href="#" class="cta-buttons a secondary-button">See How It Works</a>
    </div>
    ''', unsafe_allow_html=True)
    
    # Microphone Icon
    st.markdown('<div class="microphone-icon text-center">🎤</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

    # Adding functionality to the buttons
    col1, col2 = st.columns([1,1])
    with col1:
        if st.button("Start Transcribing", use_container_width=True):
            st.switch_page("pages/transcribe.py")
    
    with col2:
        if st.button("How It Works", use_container_width=True):
            st.info("""
            AudioScribe makes transcription super easy:
            1. Click 'Start Transcribing'
            2. Either upload an audio file or record directly
            3. Our AI instantly converts your audio to text
            4. Edit, copy, or save your transcription
            """)

elif page == "Upload Audio":
    st.subheader("Upload Audio File")
    uploaded_file = st.file_uploader("Choose an audio file", type=SUPPORTED_FORMATS)
    if uploaded_file:
        valid, message = validate_file(uploaded_file)
        if not valid:
            st.error(message)
        elif st.button("Transcribe Uploaded Audio"):
            processed_file = convert_to_wav(uploaded_file)
            if processed_file:
                success, result = transcribe_audio(processed_file)
                if success:
                    st.subheader("Transcription")
                    st.write(result)
                else:
                    st.error(result)

elif page == "Record Audio":
    st.subheader("Record Audio")
    audio_data = st.audio_input("Record your audio")
    if audio_data:
        st.success("Audio recorded successfully!")
        if st.button("Transcribe Recorded Audio"):
            audio_data.seek(0)
            success, result = transcribe_audio(audio_data)
            if success:
                st.subheader("Transcription")
                st.write(result)
            else:
                st.error(result)

elif page == "About":
    st.subheader("About AudioInk")
    st.markdown('''
    :red[AudioInk is an AI-powered transcription tool that allows users to record or upload audio and get real-time transcription using Azure Whisper AI. 
    Built using Streamlit, it offers a simple and efficient way to convert speech to text.]
    ''')
st.caption("Powered by Azure Whisper AI")
