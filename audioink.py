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

# API Configuration
AZURE_WHISPER_API_URL = "https://your-api-endpoint.azure.com"
API_KEY = "your_api_key_here"
SUPPORTED_FORMATS = ["mp3", "mp4", "mpeg", "mpga", "m4a", "wav", "webm"]

# Function to validate file
def validate_file(file):
    if file.size > 25 * 1024 * 1024:
        return False, "File size exceeds 25MB. Please upload a smaller file."
    return True, ""

# Function to transcribe audio
def transcribe_audio(audio_file):
    headers = {"api-key": API_KEY, "Authorization": f"Bearer {API_KEY}"}
    audio_file.seek(0)
    files = {"file": (audio_file.name, audio_file, "audio/wav")}
    
    response = requests.post(AZURE_WHISPER_API_URL, headers=headers, files=files, timeout=60)
    
    if response.status_code == 200:
        transcription = response.json().get("text", "No text returned")
        return True, transcription
    else:
        return False, f"API Error: {response.status_code} - {response.text}"

# Streamlit UI
def main():
    st.title("AudioInk - AI-Powered Transcription")
    
    uploaded_file = st.file_uploader("Upload an audio file", type=SUPPORTED_FORMATS)
    if uploaded_file:
        valid, message = validate_file(uploaded_file)
        if not valid:
            st.error(message)
        else:
            if st.button("Transcribe Audio"):
                success, result = transcribe_audio(uploaded_file)
                if success:
                    st.subheader("Transcription Result")
                    st.text_area("Transcribed Text", value=result, height=200)
                    
                    # Provide a download option
                    txt_bytes = BytesIO(result.encode("utf-8"))
                    st.download_button(
                        label="Download Transcription",
                        data=txt_bytes,
                        file_name="transcription.txt",
                        mime="text/plain"
                    )
                else:
                    st.error(result)

if __name__ == "__main__":
    main()
