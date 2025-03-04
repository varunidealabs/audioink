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
        .stApp { 
            background-color: #f8f8fb; 
            font-family: 'Inter', sans-serif; 
        }
        .main-container {
            max-width: 800px;
            margin: 0 auto;
            padding: 2rem;
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
            font-size: 1.5rem;
            color: #637082;
            max-width: 700px;
            margin: 0 auto 2rem;
        }
        .transcribe-container {
            background-color: white;
            border-radius: 15px;
            padding: 2rem;
            box-shadow: 0 10px 25px rgba(0,0,0,0.1);
        }
        .how-it-works {
            background-color: #f0f4f8;
            border-radius: 15px;
            padding: 1.5rem;
            margin-top: 1rem;
        }
    </style>
""", unsafe_allow_html=True)

# API Configuration
AZURE_WHISPER_API_URL = st.secrets.get("AZURE_WHISPER_API_URL", "https://your-api-endpoint.azure.com")
API_KEY = st.secrets.get("AZURE_API_KEY", "your_api_key_here")
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

# Main App
def main():
    # Select page
    page = st.radio("Navigate", 
        ["Home", "Transcribe", "How It Works", "FAQ"], 
        horizontal=True
    )

    if page == "Home":
        home_page()
    elif page == "Transcribe":
        transcribe_page()
    elif page == "How It Works":
        how_it_works_page()
    elif page == "FAQ":
        faq_page()

def home_page():
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
    AudioInk converts voice notes into text that's easy to read and ready to share.
    Create meeting notes, memos, emails, articles and more. 
    All you have to do is talk.
    </p>
    ''', unsafe_allow_html=True)
    
    # CTA Buttons
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(
            '<a href="#" class="primary-button" style="display:block; text-align:center; padding:12px; background-color:#ff5722; color:white; text-decoration:none; border-radius:50px;">Start Transcribing</a>', 
            unsafe_allow_html=True
        )
    with col2:
        st.markdown(
            '<a href="#" class="secondary-button" style="display:block; text-align:center; padding:12px; background-color:#f0f0f5; color:#2c3e50; text-decoration:none; border-radius:50px;">See How It Works</a>', 
            unsafe_allow_html=True
        )
    
    st.markdown('</div>', unsafe_allow_html=True)

def transcribe_page():
    st.markdown('<div class="transcribe-container">', unsafe_allow_html=True)
    st.header("Transcribe Your Audio")
    
    # Tabs for different input methods
    tab1, tab2 = st.tabs(["Upload Audio", "Record Audio"])
    
    with tab1:
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
    
    with tab2:
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
    
    st.markdown('</div>', unsafe_allow_html=True)

def how_it_works_page():
    st.markdown('<div class="how-it-works">', unsafe_allow_html=True)
    st.header("How AudioInk Works")
    
    # Steps explanation
    steps = [
        "Choose your input method: Upload or Record",
        "Select your audio file or record audio",
        "Click 'Transcribe'",
        "Get instant, accurate text transcription"
    ]
    
    for i, step in enumerate(steps, 1):
        st.markdown(f"""
        <div style="display:flex; align-items:center; margin-bottom:1rem;">
            <div style="background-color:#ff5722; color:white; width:40px; height:40px; border-radius:50%; display:flex; align-items:center; justify-content:center; margin-right:1rem;">
                {i}
            </div>
            <span style="font-size:1.1rem;">{step}</span>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

def faq_page():
    st.header("Frequently Asked Questions")
    
    faqs = [
        ("What audio formats are supported?", "We support MP3, MP4, WAV, M4A, and more."),
        ("Is there a file size limit?", "Yes, the maximum file size is 25MB."),
        ("How accurate is the transcription?", "Our AI-powered transcription is highly accurate."),
        ("Is my audio data secure?", "Yes, we use secure, encrypted processing.")
    ]
    
    for question, answer in faqs:
        with st.expander(question):
            st.write(answer)

if __name__ == "__main__":
    main()
