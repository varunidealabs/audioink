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

page = st.sidebar.radio("Navigation", ["Home", "Upload Audio", "Record Audio", "About"], index=0)


if page=="Home":
    # Custom CSS for enhanced typography and colors
    st.markdown("""
    <style>
        .crazy-title {
            font-family: 'Impact', sans-serif;
            color: #FF6B6B;
            text-align: center;
            font-size: 3.5em;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
            margin-bottom: 20px;
        }
        .crazy-subtitle {
            font-family: 'Courier New', monospace;
            color: #4ECDC4;
            text-align: center;
            font-size: 1.5em;
            font-style: italic;
            margin-bottom: 30px;
        }
        .section-header {
            font-family: 'Arial Black', sans-serif;
            color: #FF6B6B;
            font-size: 1.8em;
            border-bottom: 3px solid #FF6B6B;
            padding-bottom: 10px;
            margin-top: 20px;
        }
        .emoji-list {
            font-family: 'Arial', sans-serif;
            color: #2A9D8F;
            font-size: 1.2em;
            line-height: 1.6;
        }
        .warning-section {
            background-color: #FFD93D;
            padding: 20px;
            border-radius: 15px;
            margin: 20px 0;
        }
        .disclaimer {
            font-family: 'Comic Sans MS', cursive;
            color: #6A5ACD;
            font-style: italic;
            text-align: center;
            margin-top: 20px;
        }
    </style>
    """, unsafe_allow_html=True)

    # Crazy Title
    st.markdown('<h1 class="crazy-title">🎙️ AudioScribe</h1>', unsafe_allow_html=True)
    st.markdown('<p class="crazy-subtitle">No more typing, no more lost ideas. Just talk, and boom </p>', unsafe_allow_html=True)

    # Imagine This Chaos Section
    st.markdown('<h2 class="section-header">🤪 Imagine This Chaos...</h2>', unsafe_allow_html=True)
    st.markdown("""
    <div class="emoji-list">
    AudioPen converts voice notes into text that's easy to read and ready to share. 
    </div>
    """, unsafe_allow_html=True)

    # Madness Explained
    st.markdown('<h2 class="section-header">The Madness Explained</h2>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ### 🎤 Record Mode
        - Just. Start. Talking. 
        - No judgment zone! 
        - Speak like nobody's listening
        - Turn brain's wild stream of consciousness into readable text
        """)
    
    with col2:
        st.markdown("""
        ### 📁 Upload Mode
        - Got an old voice memo? 
        - Random audio file collecting dust? 
        - Grandpa's legendary story? 
        - WE. WILL. DECODE. IT. 🕵️‍♀️
        """)

    # Warning Section
    st.markdown('<div class="warning-section">', unsafe_allow_html=True)
    st.markdown('<h2 class="section-header">🌈 Warning: Side Effects May Include</h2>', unsafe_allow_html=True)
    st.markdown("""
    - Sudden bursts of productivity
    - Uncontrollable feeling of being a tech wizard
    - Permanent grin from how cool transcription can be
    - Potential addiction to talking to your devices
    """)
    st.markdown('</div>', unsafe_allow_html=True)

    # Pro Tip
    st.markdown('<h2 class="section-header">🤯 Pro Tip</h2>', unsafe_allow_html=True)
    st.markdown("""
    Our AI doesn't just transcribe. It understands your chaotic brilliance. 
    Mumble, stutter, use bizarre analogies - we'll turn it into Shakespeare-level prose! 
    (Okay, maybe not Shakespeare, but definitely coherent text)
    """)

    # Disclaimer
    st.markdown('<p class="disclaimer">🎤 SPEAK. WE LISTEN. MAGIC HAPPENS. 🔮</p>', unsafe_allow_html=True)
    st.markdown('<p class="disclaimer">AudioScribe is not responsible for world-changing ideas or podcaster ambitions!</p>', unsafe_allow_html=True)

elif page == "Upload Audio":
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
    st.markdown('''
    red[AudioInk is an AI-powered transcription tool that allows users to record or upload audio and get real-time transcription using Azure Whisper AI. 
    Built using Streamlit, it offers a simple and efficient way to convert speech to text.
]
    ''')
st.caption("Powered by Azure Whisper AI")
