import os
import requests
import streamlit as st
from io import BytesIO
from pydub import AudioSegment
from pydub.utils import which

# Automatically set FFmpeg paths
AudioSegment.converter = which("ffmpeg")
AudioSegment.ffmpeg = which("ffmpeg")
AudioSegment.ffprobe = which("ffprobe")

# Page Configuration
st.set_page_config(
    page_title="AudioScribe", 
    page_icon="🎙️", 
    layout="centered"
)

# Custom CSS for modern, clean design
st.markdown("""
    <style>
        .stApp {
            background-color: #f4f4f8;
            font-family: 'Inter', sans-serif;
        }
        .main-container {
            max-width: 600px;
            margin: 0 auto;
            padding: 2rem;
            background-color: white;
            border-radius: 16px;
            box-shadow: 0 10px 25px rgba(0,0,0,0.1);
        }
        .stButton>button {
            background-color: #007bff;
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 8px;
            font-weight: 600;
            transition: all 0.3s ease;
        }
        .stButton>button:hover {
            background-color: #0056b3;
            transform: translateY(-2px);
        }
        .transcript-box {
            background-color: #f8f9fa;
            border-radius: 10px;
            padding: 20px;
            margin-top: 20px;
        }
    </style>
""", unsafe_allow_html=True)

# Load API credentials securely
AZURE_WHISPER_API_URL = st.secrets["AZURE_WHISPER_API_URL"]
API_KEY = st.secrets["AZURE_API_KEY"]

# Constants from original backend
SUPPORTED_FORMATS = ["mp3", "mp4", "mpeg", "mpga", "m4a", "wav", "webm"]
MAX_FILE_SIZE = 25 * 1024 * 1024  # 25MB
MAX_RECORDING_DURATION = 5 * 60  # 5 minutes (adjustable)

# Function to Transcribe Audio (directly from backend)
def transcribe_audio(audio_file):
    headers = {"api-key": API_KEY, "Authorization": f"Bearer {API_KEY}"}
    try:
        with st.spinner("Transcribing audio..."):
            audio_file.seek(0)
            files = {"file": (audio_file.name, audio_file, "audio/wav")}
            response = requests.post(AZURE_WHISPER_API_URL, headers=headers, files=files, timeout=60)

            if response.status_code == 200:
                return response.json().get("text", "No text returned from API")
            else:
                st.error(f"API Error: {response.status_code} - {response.text}")
                return None
    except requests.exceptions.RequestException as e:
        st.error(f"Error: {str(e)}")
        return None

# Validate File (from backend)
def validate_file(file):
    if not file:
        return False, "No file uploaded."
    if file.size > MAX_FILE_SIZE:
        return False, "File too large. Max size is 25MB."
    if file.name.split(".")[-1].lower() not in SUPPORTED_FORMATS:
        return False, "Unsupported file format."
    return True, "File is valid."

# Convert Audio to WAV (from backend)
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

# Main App
def main():
    st.markdown("""
        <div class="main-container">
            <h1 style="text-align: center; color: #333;">🎙️ AudioScribe</h1>
            <p style="text-align: center; color: #666;">Transcribe audio instantly</p>
        </div>
    """, unsafe_allow_html=True)

    # Tabs for different input methods
    tab1, tab2 = st.tabs(["📤 Upload Audio", "🎤 Record Audio"])

    with tab1:
        st.markdown("<div class='main-container'>", unsafe_allow_html=True)
        uploaded_file = st.file_uploader(
            "Choose an audio file", 
            type=SUPPORTED_FORMATS,
            help="Upload an audio file to transcribe"
        )

        if uploaded_file is not None:
            # Validate file
            valid, message = validate_file(uploaded_file)
            if not valid:
                st.error(message)
            elif st.button("Transcribe Uploaded Audio", key="upload_transcribe"):
                # Convert and transcribe
                processed_file = convert_to_wav(uploaded_file)
                if processed_file:
                    transcription = transcribe_audio(processed_file)
                    
                    if transcription:
                        st.markdown("""
                            <div class="transcript-box">
                                <h3>Transcription</h3>
                        """, unsafe_allow_html=True)
                        st.write(transcription)
                        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with tab2:
        st.markdown("<div class='main-container'>", unsafe_allow_html=True)
        st.write("Click the button below to start recording")
        
        # Audio recording placeholder
        recorded_audio = st.audio_input("Record Audio")

        if recorded_audio is not None:
            if st.button("Transcribe Recorded Audio", key="record_transcribe"):
                transcription = transcribe_audio(recorded_audio)
                
                if transcription:
                    st.markdown("""
                        <div class="transcript-box">
                            <h3>Transcription</h3>
                    """, unsafe_allow_html=True)
                    st.write(transcription)
                    st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    st.caption("Powered by Azure Whisper API")

if __name__ == "__main__":
    main()
