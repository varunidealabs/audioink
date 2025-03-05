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
        .cta-buttons {
            display: flex;
            gap: 1.5rem;
            justify-content: center;
            margin-bottom: 2rem;
        }
        .cta-button {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            padding: 15px 30px;
            border-radius: 50px;
            font-weight: 600;
            background-color: #ff5722;
            color: white;
            text-decoration: none;
            transition: all 0.3s ease;
            box-shadow: 0 10px 20px rgba(255,87,34,0.2);
        }
        .transcription-container {
            background-color: white;
            border-radius: 15px;
            padding: 2rem;
            box-shadow: 0 10px 25px rgba(0,0,0,0.1);
            margin-top: 2rem;
        }
        .drag-drop-area {
            border: 2px dashed #ff5722;
            border-radius: 10px;
            padding: 2rem;
            text-align: center;
            margin-bottom: 1rem;
        }
    </style>
""", unsafe_allow_html=True)

# API Configuration
AZURE_WHISPER_API_URL = st.secrets.get("AZURE_WHISPER_API_URL", "https://your-api-endpoint.azure.com")
API_KEY = st.secrets.get("AZURE_API_KEY", "your_api_key_here")
SUPPORTED_FORMATS = ["mp3", "mp4", "mpeg", "mpga", "m4a", "wav", "webm"]
MAX_FILE_SIZE = 25 * 1024 * 1024

# Transcription Functions (Keep the same as in the original code)
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
            
            # Debug information
            st.write(f"Response Status Code: {response.status_code}")
            st.write(f"Response Content: {response.text}")
            
            if response.status_code == 200:
                transcription = response.json().get("text", "No text returned")
                return True, transcription
            else:
                return False, f"API Error: {response.status_code} - {response.text}"
    except Exception as e:
        return False, f"Transcription error: {str(e)}"

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
    
    # Columns for Upload and Record buttons
    col1, col2 = st.columns(2)
    
    with col1:
        upload_clicked = st.button("Upload Audio", key="upload_btn", use_container_width=True)
    
    with col2:
        record_clicked = st.button("Live Audio Capture", key="record_btn", use_container_width=True)
    
    # Transcription Container
    st.markdown('<div class="transcription-container">', unsafe_allow_html=True)
    
    # Upload Audio Section
    if upload_clicked:
        st.subheader("Upload Audio")
        uploaded_file = st.file_uploader("Choose an audio file", type=SUPPORTED_FORMATS)
        
        if uploaded_file:
            # Drag and Drop Area
            st.markdown('''
            <div class="drag-drop-area">
                Drag and drop file here
            </div>
            ''', unsafe_allow_html=True)
            
            # Validate File
            valid, message = validate_file(uploaded_file)
            if not valid:
                st.error(message)
            else:
                # Transcribe Button
                if st.button("Transcribe", key="upload_transcribe"):
                    # Convert to WAV
                    processed_file = convert_to_wav(uploaded_file)
                    
                    if processed_file:
                        # Attempt Transcription
                        success, result = transcribe_audio(processed_file)
                        
                        if success:
                            # Display Transcription
                            st.subheader("Transcription Result")
                            st.text_area("Transcribed Text", value=result, height=200)
                            
                            # Download Button
                            txt_filename = "transcription.txt"
                            txt_bytes = BytesIO(result.encode("utf-8"))
                            st.download_button(
                                label="Download Transcription",
                                data=txt_bytes,
                                file_name=txt_filename,
                                mime="text/plain"
                            )
                        else:
                            # Error Handling
                            st.error(result)
    
    # Record Audio Section
    if record_clicked:
        st.subheader("Live Audio Capture")
        audio_data = st.audio_input("Record your audio")
        
        if audio_data:
            st.success("Audio recorded successfully!")
            
            if st.button("Transcribe Recorded Audio", key="record_transcribe"):
                # Attempt Transcription
                success, result = transcribe_audio(audio_data)
                
                if success:
                    # Display Transcription
                    st.subheader("Transcription Result")
                    st.text_area("Transcribed Text", value=result, height=200)
                    
                    # Download Button
                    txt_filename = "transcription.txt"
                    txt_bytes = BytesIO(result.encode("utf-8"))
                    st.download_button(
                        label="Download Transcription",
                        data=txt_bytes,
                        file_name=txt_filename,
                        mime="text/plain"
                    )
                else:
                    # Error Handling
                    st.error(result)
    
    st.markdown('</div>', unsafe_allow_html=True)
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
