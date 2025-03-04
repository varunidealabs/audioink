import os
import requests
import streamlit as st
from io import BytesIO
from pydub import AudioSegment
from pydub.utils import which

#  Automatically set FFmpeg paths
AudioSegment.converter = which("ffmpeg")
AudioSegment.ffmpeg = which("ffmpeg")
AudioSegment.ffprobe = which("ffprobe")

#  Streamlit Page Config
st.set_page_config(page_title="AudioInk", page_icon="🎙️", layout="centered")

#  Background Color
st.markdown(
    """
    <style>
        .stApp { background-color: #072842; }
    </style>
    """,
    unsafe_allow_html=True
)

#  Load API credentials securely
AZURE_WHISPER_API_URL = st.secrets["AZURE_WHISPER_API_URL"]
API_KEY = st.secrets["AZURE_API_KEY"]

#  Constants
SUPPORTED_FORMATS = ["mp3", "mp4", "mpeg", "mpga", "m4a", "wav", "webm"]
MAX_FILE_SIZE = 25 * 1024 * 1024  # 25MB
MAX_RECORDING_DURATION = 5 * 60  # 5 minutes (adjustable)

#  Function to Transcribe Audio
def transcribe_audio(audio_file):
    headers = {"api-key": API_KEY, "Authorization": f"Bearer {API_KEY}"}
    try:
        with st.spinner("Transcribing audio..."):
            audio_file.seek(0)
            files = {"file": (audio_file.name, audio_file, "audio/wav")}
            response = requests.post(AZURE_WHISPER_API_URL, headers=headers, files=files, timeout=60)

            if response.status_code == 200:
                return True, response.json().get("text", "No text returned from API")
            else:
                return False, f"API Error: {response.status_code} - {response.text}"
    except requests.exceptions.RequestException as e:
        return False, f"Error: {str(e)}"

#  Validate File
def validate_file(file):
    if not file:
        return False, "No file uploaded."
    if file.size > MAX_FILE_SIZE:
        return False, "File too large. Max size is 25MB."
    if file.name.split(".")[-1].lower() not in SUPPORTED_FORMATS:
        return False, "Unsupported file format."
    return True, "File is valid."

#  Convert Audio to WAV
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

# Record Audio (Future Improvement: Use Web Recorder)
def record_audio():
    return st.audio_input("Record your audio")

#  Main Streamlit App
def main():
    st.title("🎙️ Audio Transcription App")
    st.write("Record or upload audio to transcribe using Azure Whisper API.")

    tab1, tab2 = st.tabs(["Upload Audio", "Record Audio"])

    with tab1:
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
        audio_data = record_audio()
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

    st.caption("Powered by Azure Whisper API")

if __name__ == "__main__":
    main()
