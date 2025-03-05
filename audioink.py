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

# Page Config
st.set_page_config(page_title="AudioInk", page_icon="🎙️", layout="wide")

# Custom CSS Styling
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&display=swap');

        .stApp { 
            background-color: #f8f8fb; 
            font-family: 'Inter', sans-serif; 
        }
        .main-container {
            max-width: 800px;
            margin: 0 auto;
            padding: 4rem 2rem;
            text-align: left;
        }
        .hero-title {
            font-size: 3.5rem;
            font-weight: 800;
            color: #2c3e50;
            line-height: 1.2;
            margin-bottom: 1rem;
            margin-top: -20px;
        }
        .highlight {
            color: #ff5722;
        }
        .subtitle {
            font-size: 1.25rem;
            color: #637082;
            max-width: 700px;
            margin: 0 auto 2rem;
        }
        .transcription-area {
            background-color: white;
            border: 1px solid #e0e0e0;
            border-radius: 10px;
            padding: 1rem;
            margin-top: 1rem;
            min-height: 200px;
            text-align: left;
        }
        
        /* Water Wave Animation */
        .water-round-container {
            margin: 0;
            overflow: hidden;
            position: relative;
            width: 200px;
            height: 200px;
            border-radius: 50%;
            border: 3px solid silver;
            text-align: center;
            line-height: 50px;
            animation: water-waves linear infinite;
        }
        .water-wave1 {
            position: absolute;
            top: 40%;
            left: -25%;
            background: #FF5C0A;
            opacity: 0.7;
            width: 200%;
            height: 200%;
            border-radius: 40%;
            animation: inherit;
            animation-duration: 5s;
        }
        .water-wave2 {
            position: absolute;
            top: 45%;
            left: -35%;
            background: #FF5C0A;
            opacity: 0.5;
            width: 200%;
            height: 200%;
            border-radius: 35%;
            animation: inherit;
            animation-duration: 7s;
        }
        .water-wave3 {
            position: absolute;
            top: 50%;
            left: -35%;
            background: #FF5C0A;
            opacity: 0.3;
            width: 200%;
            height: 200%;
            border-radius: 33%;
            animation: inherit;
            animation-duration: 11s;
        }
        @keyframes water-waves {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
    </style>
""", unsafe_allow_html=True)

# API Configuration
AZURE_WHISPER_API_URL = st.secrets.get("AZURE_WHISPER_API_URL", "https://your-api-endpoint.azure.com")
API_KEY = st.secrets.get("AZURE_API_KEY", "your_api_key_here")
SUPPORTED_FORMATS = ["mp3", "mp4", "mpeg", "mpga", "m4a", "wav", "webm"]
MAX_FILE_SIZE = 25 * 1024 * 1024

def transcribe_audio(audio_file):
    headers = {
        "api-key": API_KEY, 
        "Authorization": f"Bearer {API_KEY}"
    }
    try:
        audio_file.seek(0)
        files = {"file": (audio_file.name, audio_file, "audio/wav")}
        
        with st.spinner("Transcribing audio..."):
            response = requests.post(
                AZURE_WHISPER_API_URL, 
                headers=headers, 
                files=files, 
                timeout=60
            )
            
            if response.status_code == 200:
                transcription = response.json().get("text", "No text returned")
                return True, transcription
            else:
                return False, f"API Error: {response.status_code} - {response.text}"
    except Exception as e:
        return False, f"Transcription error: {str(e)}"

def validate_file(file):
    if not file:
        return False, "No file uploaded."
    if file.size > MAX_FILE_SIZE:
        return False, "File too large. Max size is 25MB."
    if file.name.split(".")[-1].lower() not in SUPPORTED_FORMATS:
        return False, "Unsupported file format."
    return True, "File is valid."

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

def main():

    # Add Water Wave Animation 
    col1, col2 = st.columns([1, 3])
    with col1:
        # Hero Title
        st.markdown('''
        <h1 class="hero-title">
            Say it loud <span class="highlight">let words flow,</span><br>
            Upload with ease <span class="highlight">watch text grow.</span>
        </h1>
        ''', unsafe_allow_html=True)

        with col2:
        # Add Water Wave Animation Instead of Mic Image
        st.markdown('''
        <div class="water-round-container">
            <div class="water-wave1"></div>
            <div class="water-wave2"></div>
            <div class="water-wave3"></div>
        </div>
        ''', unsafe_allow_html=True)
    
    # Subtitle
    st.markdown('''
    <p class="subtitle">
    AudioInk transforms your voice into clear, shareable text.
    Create meeting notes, memos, emails, articles and more. 
    All you have to do is talk.
    </p>
    ''', unsafe_allow_html=True)
    
    # Input Mode Selection
    input_mode = st.radio(
        "Choose Input Method", 
        ["Upload Audio", "Live Audio Capture"], 
        horizontal=True
    )

    # Transcription Result Container
    transcription_result = None

    # Upload Audio Section
    if input_mode == "Upload Audio":
        uploaded_file = st.file_uploader(
            "Drag and drop or choose an audio file", 
            type=SUPPORTED_FORMATS
        )
        
        if uploaded_file:
            # Validate File
            valid, message = validate_file(uploaded_file)
            if not valid:
                st.error(message)
            
            # Transcribe Button
            if st.button("Transcribe", key="upload_transcribe"):
                # Convert to WAV
                processed_file = convert_to_wav(uploaded_file)
                
                if processed_file:
                    # Attempt Transcription
                    success, result = transcribe_audio(processed_file)
                    
                    if success:
                        transcription_result = result

    # Record Audio Section
    elif input_mode == "Live Audio Capture":
        audio_data = st.audio_input("Record your audio")
        
        if audio_data:
            st.success("Audio recorded successfully!")
            
            if st.button("Transcribe Recorded Audio", key="record_transcribe"):
                # Attempt Transcription
                success, result = transcribe_audio(audio_data)
                
                if success:
                    transcription_result = result

    # Display Transcription Result
    if transcription_result:
        st.markdown("### Transcription Result")
        
        # Large text area for transcription
        transcribed_text = st.text_area(
            "Transcribed Text", 
            value=transcription_result, 
            height=250
        )
        
        # Download Button
        txt_filename = "transcription.txt"
        txt_bytes = BytesIO(transcription_result.encode("utf-8"))
        st.download_button(
            label="Download Transcription",
            data=txt_bytes,
            file_name=txt_filename,
            mime="text/plain"
        )

    st.markdown('</div>', unsafe_allow_html=True)

    # Footer
    st.markdown("""
    <footer style="text-align:center; margin-top:2rem; color:#637082;">
        AudioInk™ built by <a href="https://idealabs.fyi" target="_blank">Ideal Labs</a> | 
        <a href="#privacy-policy">Privacy Policy</a> | 
        <a href="#terms-of-use">Terms of Use</a>
    </footer>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
