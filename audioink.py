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
def local_css():
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&display=swap');
        .stApp { 
            background-color: #f8f8fb; 
            font-family: 'Inter', sans-serif; 
        }
        .header-container {
            display: flex;
            align-items: center;
            gap: 1rem;
            margin-bottom: 2rem;
        }
        .app-title {
            font-size: 3rem;
            font-weight: 800;
            color: #FF5C0A;
            text-align: left;
            letter-spacing: -2px;
            margin: 0;
        }
        .water-round-container {
            width: 80px;
            height: 80px;
            position: relative;
            overflow: hidden;
            border-radius: 50%;
            border: 2px solid silver;
            animation: water-waves linear 10s infinite;
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
        @keyframes wave1 {
            0%, 100% { transform: translateX(0) translateY(0) rotate(0deg); }
            50% { transform: translateX(10%) translateY(-10%) rotate(180deg); }
        }
        @keyframes wave2 {
            0%, 100% { transform: translateX(0) translateY(0) rotate(0deg); }
            50% { transform: translateX(-10%) translateY(10%) rotate(-180deg); }
        }
        @keyframes wave3 {
            0%, 100% { transform: translateX(0) translateY(0) rotate(0deg); }
            50% { transform: translateX(5%) translateY(-5%) rotate(90deg); }
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
            text-align: left;
        }
        
        /* Custom toggle button styling */
        /* Custom styling for the button container */
        div[data-testid="column"] [data-testid="stButton"] {
            max-width: 180px;
            margin: 0 auto;
        }
        
        /* Style improvements for the file uploader */
        .uploadedFile {
            border-radius: 10px !important;
            border: 2px dashed #e2e8f0 !important;
        }
        
        /* Adjust spacing for better visual hierarchy */
        div.stButton > button {
            font-weight: 500;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }
        
        /* Styling for the audio input section */
        div[data-testid="stAudioInput"] {
            border-radius: 10px;
            margin-top: 8px;
        }
        
        /* Add subtle animation to active elements */
        div[data-testid="stButton"] > button[data-testid="baseButton-primary"] {
            transition: all 0.3s ease;
            transform: scale(1.02);
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
    # Apply custom CSS
    local_css()
    
    # Initialize session state to track which mode is active
    if 'active_mode' not in st.session_state:
        st.session_state.active_mode = None
    
    # Header Container with Logo and Title
    st.markdown('''
    <div class="header-container">
        <div class="water-round-container">
            <div class="water-wave1"></div>
            <div class="water-wave2"></div>
            <div class="water-wave3"></div>
        </div>
        <div class="app-title">AUDIO INK</div>
    </div>
    ''', unsafe_allow_html=True)
    
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
    
    # Custom Toggle Buttons
    st.markdown("<p>Choose Input Method</p>", unsafe_allow_html=True)
    
    # Use columns with custom widths to make buttons narrower
    col1, col_space, col2, col_end = st.columns([1, 1, 1, 4])
    
    with col1:
        upload_btn = st.button("Upload Audio", 
                              key="upload_audio_btn", 
                              use_container_width=True,
                              type="primary" if st.session_state.active_mode == "upload" else "secondary")
        
    with col2:
        record_btn = st.button("Live Audio Capture", 
                              key="live_audio_btn", 
                              use_container_width=True,
                              type="primary" if st.session_state.active_mode == "record" else "secondary")
    
    # Handle button clicks to set active mode
    if upload_btn:
        st.session_state.active_mode = "upload"
    elif record_btn:
        st.session_state.active_mode = "record"
        
    # Transcription Result Container
    transcription_result = None

    # Upload Audio Section
    if st.session_state.active_mode == "upload":
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
                    else:
                        st.error(result)

    # Record Audio Section
    elif st.session_state.active_mode == "record":
        audio_data = st.audio_input("Record your audio")
        
        if audio_data:
            st.success("Audio recorded successfully!")
            
            if st.button("Transcribe Recorded Audio", key="record_transcribe"):
                # Attempt Transcription
                success, result = transcribe_audio(audio_data)
                
                if success:
                    transcription_result = result
                else:
                    st.error(result)

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

    # Modern Footer with App Info Card
    st.markdown("""
    <div style="margin-top: 4rem;">
        <div style="max-width: 800px; margin: 0 auto; background-color: #f3f4f6; border-radius: 12px; padding: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.05);">
            <div style="display: flex; align-items: center; margin-bottom: 15px;">
                <div style="width: 40px; height: 40px; position: relative; overflow: hidden; border-radius: 50%; margin-right: 15px; background: linear-gradient(135deg, #FF5C0A 0%, #FF8F53 100%);">
                </div>
                <div>
                    <h3 style="margin: 0; color: #2c3e50; font-size: 18px;">AudioInk</h3>
                    <p style="margin: 0; color: #637082; font-size: 14px;">Voice to text, simplified.</p>
                </div>
            </div>
            <div style="display: flex; justify-content: space-between; border-top: 1px solid #e2e8f0; padding-top: 15px; font-size: 14px;">
                <div style="color: #637082;">
                    Built by <a href="https://idealabs.fyi" target="_blank" style="color: #FF5C0A; text-decoration: none;">Ideal Labs</a>
                </div>
                <div>
                    <a href="#privacy-policy" style="color: #637082; margin-right: 15px; text-decoration: none;">Privacy</a>
                    <a href="#terms-of-use" style="color: #637082; text-decoration: none;">Terms</a>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
