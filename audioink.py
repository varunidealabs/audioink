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
            max-width: 1000px;
            margin: 0 auto;
            padding: 4rem 2rem;
            text-align: center;
        }
        .hero-section {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            gap: 2rem;
        }
        .hero-title {
            font-size: 4rem;
            font-weight: 800;
            color: #2c3e50;
            line-height: 1.2;
            max-width: 800px;
        }
        .highlight {
            color: #ff5722;
        }
        .subtitle {
            font-size: 1.25rem;
            color: #637082;
            max-width: 700px;
            margin-bottom: 2rem;
        }
        .cta-buttons {
            display: flex;
            gap: 1.5rem;
            justify-content: center;
        }
        .cta-button {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            padding: 15px 30px;
            border-radius: 50px;
            font-weight: 600;
            text-decoration: none;
            transition: all 0.3s ease;
            box-shadow: 0 10px 20px rgba(255,87,34,0.2);
        }
        .primary-button {
            background-color: #ff5722;
            color: white;
        }
        .modal {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.7);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 1000;
        }
        .modal-content {
            background: white;
            padding: 2rem;
            border-radius: 15px;
            max-width: 500px;
            width: 100%;
            text-align: center;
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
    st.markdown('<div class="main-container">', unsafe_allow_html=True)
    st.markdown('<div class="hero-section">', unsafe_allow_html=True)

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
    
    # CTA Buttons with JavaScript for Modal
    st.markdown('''
    <div class="cta-buttons">
        <a href="#" class="cta-button primary-button" onclick="openModal('upload')">Start Transcribing</a>
        <a href="#" class="cta-button primary-button" onclick="openModal('record')">Live Audio Capture</a>
    </div>
    
    <script>
    function openModal(type) {
        const modal = document.createElement('div');
        modal.className = 'modal';
        modal.innerHTML = `
            <div class="modal-content">
                <h2>${type === 'upload' ? 'Upload Audio' : 'Record Audio'}</h2>
                <div id="modalContent"></div>
            </div>
        `;
        document.body.appendChild(modal);
        
        modal.onclick = function(event) {
            if (event.target == modal) {
                document.body.removeChild(modal);
            }
        };
        
        window.handleModalClose = function() {
            document.body.removeChild(modal);
        };
    }
    </script>
    ''', unsafe_allow_html=True)

    # Modal Content Handling
    audio_data = None
    transcription_text = None
    
    # Upload Modal Functionality
    uploaded_file = st.file_uploader("Choose an audio file", type=SUPPORTED_FORMATS, key="upload_modal")
    if uploaded_file:
        valid, message = validate_file(uploaded_file)
        if not valid:
            st.error(message)
        elif st.button("Transcribe Uploaded Audio"):
            processed_file = convert_to_wav(uploaded_file)
            if processed_file:
                success, result = transcribe_audio(processed_file)
                if success:
                    transcription_text = result
                    st.success("Transcription Complete!")
                    st.write(transcription_text)
                else:
                    st.error(result)

    # Record Audio Modal Functionality
    audio_data = st.audio_input("Record your audio", key="record_modal")
    if audio_data:
        st.success("Audio recorded successfully!")
        if st.button("Transcribe Recorded Audio"):
            audio_data.seek(0)
            success, result = transcribe_audio(audio_data)
            if success:
                transcription_text = result
                st.success("Transcription Complete!")
                st.write(transcription_text)
            else:
                st.error(result)

    # Download Button
    if transcription_text:
        txt_filename = "transcription.txt"
        txt_bytes = BytesIO(transcription_text.encode("utf-8"))
        st.download_button(label="Download Transcription",
                           data=txt_bytes,
                           file_name=txt_filename,
                           mime="text/plain")

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
