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
            text-align: center;
        }
        .hero-title {
            font-size: 3.5rem;
            font-weight: 800;
            color: #2c3e50;
            line-height: 1.2;
            margin-bottom: 1rem;
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
            background-color: #f0f0f0;
            border-radius: 10px;
            padding: 1rem;
            margin-top: 1rem;
            text-align: left;
            min-height: 150px;
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
                return transcription
            else:
                st.error(f"API Error: {response.status_code}")
                return None
    except Exception as e:
        st.error(f"Transcription error: {str(e)}")
        return None

def main():
    st.markdown('<div class="main-container">', unsafe_allow_html=True)

    # Hero Title
    st.markdown('''
    <h1 class="hero-title">
        Say it loud <span class="highlight">let words flow,</span><br>
        Upload with ease <span class="highlight">watch text grow.</span>
    </h1>
    ''', unsafe_allow_html=True)
    
    # Subtitle
    st.markdown('''
    <p class="subtitle">
    AudioInk transforms your voice into clear, shareable text.
    Create meeting notes, memos, emails, articles and more. 
    All you have to do is talk.
    </p>
    ''', unsafe_allow_html=True)
    
    # Audio Input Mode Selection
    input_mode = st.radio(
        "Choose Input Method", 
        ["Upload Audio", "Live Audio Capture"], 
        horizontal=True
    )

    # Transcription Container
    transcription_text = None

    if input_mode == "Upload Audio":
        uploaded_file = st.file_uploader(
            "Drag and drop file here", 
            type=SUPPORTED_FORMATS
        )
        
        if uploaded_file:
            if st.button("Transcribe"):
                # Convert to WAV if needed
                try:
                    audio_wav = uploaded_file
                    if uploaded_file.name.split('.')[-1].lower() != 'wav':
                        audio_bytes = uploaded_file.read()
                        uploaded_file.seek(0)
                        audio = AudioSegment.from_file(
                            BytesIO(audio_bytes), 
                            format=uploaded_file.name.split('.')[-1]
                        )
                        wav_io = BytesIO()
                        audio.export(wav_io, format="wav")
                        wav_io.seek(0)
                        wav_io.name = "converted.wav"
                        audio_wav = wav_io

                    # Transcribe
                    transcription_text = transcribe_audio(audio_wav)
                except Exception as e:
                    st.error(f"Conversion error: {str(e)}")

    else:  # Live Audio Capture
        audio_data = st.audio_input("Record your audio")
        
        if audio_data:
            if st.button("Transcribe Recorded Audio"):
                transcription_text = transcribe_audio(audio_data)

    # Display Transcription
    if transcription_text:
        st.markdown("### Transcription Result")
        st.markdown(
            f'<div class="transcription-area">{transcription_text}</div>', 
            unsafe_allow_html=True
        )
        
        # Download Button
        txt_filename = "transcription.txt"
        txt_bytes = BytesIO(transcription_text.encode("utf-8"))
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
