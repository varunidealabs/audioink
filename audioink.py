import streamlit as st
import requests
import os
from io import BytesIO
from pydub import AudioSegment
from pydub.utils import which
from PIL import Image

# Set FFmpeg paths automatically
AudioSegment.converter = which("ffmpeg")
AudioSegment.ffmpeg = which("ffmpeg")
AudioSegment.ffprobe = which("ffprobe")

# Page Configuration
st.set_page_config(page_title="AudioInk", page_icon="🎧", layout="wide")

# Constants
AZURE_WHISPER_API_URL = st.secrets.get("AZURE_WHISPER_API_URL", "https://your-api-endpoint.azure.com")
API_KEY = st.secrets.get("AZURE_API_KEY", "your_api_key_here")
SUPPORTED_FORMATS = ["mp3", "mp4", "mpeg", "mpga", "m4a", "wav", "webm"]
MAX_FILE_SIZE = 25 * 1024 * 1024

def load_css():
    """Loads custom CSS for UI styling."""
    st.markdown("""
    <style>
        .stApp { background-color: #f8f8fb; font-family: 'Inter', sans-serif; }
        .app-title { font-size: 3rem; font-weight: 800; color: #FF5C0A; }
    </style>
    """, unsafe_allow_html=True)

def validate_file(file):
    """Validates uploaded file size and format."""
    if not file:
        return False, "No file uploaded."
    if file.size > MAX_FILE_SIZE:
        return False, "File too large. Max size is 25MB."
    if file.name.split(".")[-1].lower() not in SUPPORTED_FORMATS:
        return False, "Unsupported file format."
    return True, "File is valid."

def convert_to_wav(audio_file):
    """Converts audio file to WAV format if necessary."""
    try:
        file_extension = audio_file.name.split(".")[-1].lower()
        if file_extension == "wav":
            return audio_file
        audio = AudioSegment.from_file(audio_file, format=file_extension)
        wav_io = BytesIO()
        audio.export(wav_io, format="wav")
        wav_io.seek(0)
        wav_io.name = f"{os.path.splitext(audio_file.name)[0]}.wav"
        return wav_io
    except Exception as e:
        st.error(f"Error converting audio: {str(e)}")
        return None

def transcribe_audio(audio_file):
    """Sends an audio file to the API for transcription."""
    headers = {"api-key": API_KEY, "Authorization": f"Bearer {API_KEY}"}
    try:
        audio_file.seek(0)
        files = {"file": (audio_file.name, audio_file, "audio/wav")}
        with st.spinner("Transcribing audio..."):
            response = requests.post(AZURE_WHISPER_API_URL, headers=headers, files=files, timeout=60)
            if response.status_code == 200:
                return True, response.json().get("text", "No text returned")
            return False, f"API Error: {response.status_code} - {response.text}"
    except Exception as e:
        return False, f"Transcription error: {str(e)}"

def main():
    load_css()
    st.markdown("<div class='app-title'>AUDIO INK</div>", unsafe_allow_html=True)
    input_mode = st.radio("Choose Input Method", ["Upload Audio", "Live Audio Capture"], horizontal=True)
    transcription_result = None

    if input_mode == "Upload Audio":
        uploaded_file = st.file_uploader("Upload an audio file", type=SUPPORTED_FORMATS)
        if uploaded_file:
            valid, message = validate_file(uploaded_file)
            if not valid:
                st.error(message)
            elif st.button("Transcribe"):
                processed_file = convert_to_wav(uploaded_file)
                if processed_file:
                    success, result = transcribe_audio(processed_file)
                    if success:
                        transcription_result = result
    
    if transcription_result:
        st.markdown("### Transcription Result")
        st.text_area("Transcribed Text", value=transcription_result, height=250)

if __name__ == "__main__":
    main()
