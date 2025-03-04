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

page = st.sidebar.radio("Navigation", ["Upload Audio", "Record Audio", "About"], index=0)

if page == "Upload Audio":
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
    st.write("AudioInk is an AI-powered transcription tool that allows users to record or upload audio and get real-time transcription using Azure Whisper AI. Built using Streamlit, it offers a simple and efficient way to convert speech to text.")

st.caption("Powered by Azure Whisper AI")
