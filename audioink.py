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
        /* Style improvements for the file uploader - these won't work as well as the inline CSS */
        .uploadedFile {
            border-radius: 12px !important;
            border: 2px dashed #FF5C0A !important;
            background-color: rgba(255, 92, 10, 0.05) !important;
            padding: 20px !important;
            transition: all 0.3s ease !important;
        }
        
        .uploadedFile:hover {
            background-color: rgba(255, 92, 10, 0.1) !important;
            border-color: #FF7D3C !important;
        }
        
        /* Styling for the audio input section - enhance the circular buttons */
        div[data-testid="stAudioInput"] {
            border-radius: 12px !important;
            border: 2px solid #FF5C0A !important;
            background-color: rgba(255, 92, 10, 0.05) !important;
            padding: 12px !important;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05) !important;
            margin-top: 8px !important;
        }
        
        div[data-testid="stAudioInput"] button {
            background-color: #FF5C0A !important;
            color: white !important;
            border-radius: 50% !important;
            width: 56px !important;
            height: 56px !important;
            box-shadow: 0 4px 10px rgba(255, 92, 10, 0.3) !important;
            transition: all 0.3s ease !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
        }
        
        div[data-testid="stAudioInput"] button:hover {
            transform: scale(1.05) !important;
            box-shadow: 0 6px 12px rgba(255, 92, 10, 0.4) !important;
        }
        
        /* Style the waveform container */
        div[data-testid="stAudioInput"] > div:nth-child(2) {
            background-color: #f8f9fa !important;
            border-radius: 8px !important;
            padding: 8px 12px !important;
        }
        
        /* Custom button styling */
        div.stButton > button {
            font-weight: 500;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
            transition: all 0.3s ease;
            border-radius: 4px;
        }
        
        div.stButton > button:hover {
            transform: translateY(-1px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
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
    st.markdown("<p>Let's try this out </p>", unsafe_allow_html=True)
    
    # Use columns to center the buttons
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        # Create a 2-column layout within the center column
        btn_col1, btn_col2 = st.columns(2)
        
        with btn_col1:
            upload_btn = st.button("Upload Audio", 
                                  key="upload_audio_btn",
                                  type="primary" if st.session_state.active_mode == "upload" else "secondary",
                                  use_container_width=True)
        
        with btn_col2:
            record_btn = st.button("Live Audio Capture", 
                                  key="live_audio_btn",
                                  type="primary" if st.session_state.active_mode == "record" else "secondary",
                                  use_container_width=True)
    
    # Handle button clicks to set active mode
    if upload_btn:
        st.session_state.active_mode = "upload"
    elif record_btn:
        st.session_state.active_mode = "record"
        
    # Transcription Result Container
    transcription_result = None

    # Upload Audio Section
    if st.session_state.active_mode == "upload":
        # Create columns to control width
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            # Create a visually appealing upload container
            st.markdown("""
            <style>
                /* Custom styling for the file uploader */
                [data-testid="stFileUploader"] {
                    width: 100%;
                }
                
                [data-testid="stFileUploader"] section {
                    border: 2px dashed #FF5C0A !important;
                    border-radius: 12px !important;
                    padding: 30px !important;
                    background-color: rgba(255, 92, 10, 0.03) !important;
                    text-align: center !important;
                    transition: all 0.3s ease !important;
                    position: relative;
                }
                
                [data-testid="stFileUploader"] section:hover {
                    background-color: rgba(255, 92, 10, 0.08) !important;
                    border-color: #FF7D3C !important;
                    transform: translateY(-2px);
                    box-shadow: 0 4px 12px rgba(255, 92, 10, 0.15);
                }
                
                /* Hide default text */
                [data-testid="stFileUploader"] section p {
                    display: none !important;
                }
                
                /* Hide the default button and recreate it */
                [data-testid="stFileUploader"] section button {
                    display: none !important;
                }
                
                /* Hide the file preview */
                .uploadedFile {
                    display: none !important;
                }
            </style>
            
            <div style="text-align: center; margin-bottom: 25px; margin-top: 10px;">
                <div style="display: inline-block; background-color: rgba(255, 92, 10, 0.1); padding: 8px 16px; border-radius: 20px;">
                    <span style="color: #FF5C0A; font-weight: 500;">Upload your audio file</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            uploaded_file = st.file_uploader(
                "Drag and drop or choose an audio file", 
                type=SUPPORTED_FORMATS
            )
            
            if uploaded_file:
                # Show file info in a custom format similar to the images
                file_size_kb = uploaded_file.size / 1024
                file_type = uploaded_file.type
                
                st.markdown(f"""
                <div style="background-color: #f8f9fa; border-radius: 10px; padding: 15px; margin: 15px 0; display: flex; align-items: center; box-shadow: 0 2px 8px rgba(0,0,0,0.06);">
                    <div style="background: #FF5C0A; width: 50px; height: 50px; border-radius: 10px; display: flex; align-items: center; justify-content: center; margin-right: 15px;">
                        <span style="color: white; font-size: 24px;">🎵</span>
                    </div>
                    <div style="flex-grow: 1;">
                        <div style="font-weight: 600; color: #2c3e50; font-size: 16px; margin-bottom: 4px;">
                            {uploaded_file.name}
                        </div>
                        <div style="display: flex; align-items: center; justify-content: space-between;">
                            <div style="font-size: 13px; color: #6c757d;">audio/mpeg</div>
                            <div style="font-size: 13px; color: #FF5C0A; font-weight: 500;">{file_size_kb:.1f} KB</div>
                        </div>
                    </div>
                </div>
                
                <div style="display: flex; justify-content: space-between; margin-top: 4px; padding: 0 5px;">
                    <div></div>
                    <div style="font-size: 13px; color: #28a745;">Ready to transcribe</div>
                </div>
                """, unsafe_allow_html=True)
                
                # Validate File
                valid, message = validate_file(uploaded_file)
                if not valid:
                    st.error(message)
                
                # Transcribe Button
                if st.button("🎧 Transcribe Now", key="upload_transcribe", use_container_width=True, type="primary"):
                    # Convert to WAV
                    with st.spinner("Converting audio..."):
                        processed_file = convert_to_wav(uploaded_file)
                    
                    if processed_file:
                        # Attempt Transcription
                        with st.spinner("Transcribing your audio..."):
                            success, result = transcribe_audio(processed_file)
                        
                        if success:
                            transcription_result = result
                        else:
                            st.error(result)

    # Record Audio Section
    elif st.session_state.active_mode == "record":
        # Create columns to control width
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            st.markdown("""
            <div style="text-align: center; margin-bottom: 15px;">
                <div style="display: inline-block; background-color: rgba(255, 92, 10, 0.1); padding: 8px 16px; border-radius: 20px;">
                    <span style="color: #FF5C0A; font-weight: 500;">Record your voice</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            audio_data = st.audio_input("Record your audio")
            
            if audio_data:
                st.markdown("""
                <div style="background-color: #e8f5e9; border-radius: 8px; padding: 12px; margin: 15px 0; border-left: 4px solid #4caf50;">
                    <div style="display: flex; align-items: center;">
                        <div style="background-color: #4caf50; width: 30px; height: 30px; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin-right: 12px;">
                            <span style="color: white; font-size: 16px;">✓</span>
                        </div>
                        <div style="font-weight: 500; color: #2e7d32;">Audio recorded successfully!</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Removed audio preview display
                
                if st.button("Transcribe Recorded Audio", key="record_transcribe", use_container_width=True):
                    # Attempt Transcription
                    with st.spinner("Processing your audio..."):
                        success, result = transcribe_audio(audio_data)
                        
                        if success:
                            transcription_result = result
                        else:
                            st.error(result)

    # Display Transcription Result
    if transcription_result:
        # Create columns to control width for the transcription result
        res_col1, res_col2, res_col3 = st.columns([1, 3, 1])
        
        with res_col2:
            st.markdown("""
            <div style="background-color: #f0f7ff; border-radius: 12px; padding: 20px; margin-top: 30px;">
                <div style="display: flex; align-items: center; margin-bottom: 15px;">
                    <div style="background-color: #2196f3; width: 40px; height: 40px; border-radius: 8px; display: flex; align-items: center; justify-content: center; margin-right: 15px;">
                        <span style="color: white; font-size: 20px;">📝</span>
                    </div>
                    <h3 style="margin: 0; color: #0d47a1; font-weight: 600;">Transcription Result</h3>
                </div>
            """, unsafe_allow_html=True)
            
            # Large text area for transcription
            transcribed_text = st.text_area(
                "Transcribed Text", 
                value=transcription_result, 
                height=250
            )
            
            # Calculate word and character count
            word_count = len(transcription_result.split())
            char_count = len(transcription_result)
            
            st.markdown(f"""
            <div style="display: flex; justify-content: space-between; margin-top: 10px; font-size: 14px; color: #637082;">
                <div>{word_count} words</div>
                <div>{char_count} characters</div>
            </div>
            """, unsafe_allow_html=True)
            
            # Action buttons
            col1, col2 = st.columns(2)
            
            with col1:
                # Copy button (simulated with download)
                if st.button("📋 Copy to Clipboard", type="secondary"):
                    st.info("Text copied to clipboard functionality would be implemented here in a full app")
            
            with col2:
                # Download Button
                txt_filename = "transcription.txt"
                txt_bytes = BytesIO(transcription_result.encode("utf-8"))
                st.download_button(
                    label="⬇️ Download Transcription",
                    data=txt_bytes,
                    file_name=txt_filename,
                    mime="text/plain"
                )
            
            st.markdown("</div>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
