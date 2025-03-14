import streamlit as st
import requests
import os
from io import BytesIO
from pydub import AudioSegment
from pydub.utils import which
from PIL import Image
import base64

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
        
        /* Custom audio recorder styling */
        .custom-audio-recorder {
            border-radius: 12px;
            border: 2px solid #FF5C0A;
            background-color: rgba(255, 92, 10, 0.05);
            padding: 20px;
            margin-top: 20px;
        }
        
        .audio-controls {
            display: flex;
            align-items: center;
            gap: 15px;
            margin-bottom: 15px;
        }
        
        .audio-button {
            background-color: #FF5C0A;
            color: white;
            border: none;
            border-radius: 50%;
            width: 56px;
            height: 56px;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            box-shadow: 0 4px 10px rgba(255, 92, 10, 0.3);
            transition: all 0.3s ease;
        }
        
        .audio-button:hover {
            transform: scale(1.05);
            box-shadow: 0 6px 12px rgba(255, 92, 10, 0.4);
        }
        
        .audio-waveform {
            height: 60px;
            background-color: #f8f9fa;
            border-radius: 8px;
            overflow: hidden;
            position: relative;
            flex-grow: 1;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        .waveform-placeholder {
            display: flex;
            align-items: center;
            gap: 5px;
            margin: 0 auto;
        }
        
        .waveform-placeholder .bar {
            width: 3px;
            background-color: #FF5C0A;
            opacity: 0.5;
            border-radius: 1px;
        }
        
        .timer {
            color: #637082;
            font-size: 14px;
            font-weight: 500;
            margin-left: 10px;
        }
        
        /* Custom file uploader styling */
        .custom-file-uploader {
            border: 2px dashed #FF5C0A;
            border-radius: 12px;
            padding: 30px;
            background-color: rgba(255, 92, 10, 0.03);
            text-align: center;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        
        .custom-file-uploader:hover {
            background-color: rgba(255, 92, 10, 0.08);
            border-color: #FF7D3C;
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(255, 92, 10, 0.15);
        }
    </style>
    """, unsafe_allow_html=True)

# Custom Audio Recorder HTML
def custom_audio_recorder():
    # Custom JavaScript for audio recording
    custom_js = """
    <script>
        // Audio Recording Variables
        let mediaRecorder;
        let audioChunks = [];
        let isRecording = false;
        let audioBlob = null;
        let audioUrl = null;
        let timerInterval = null;
        let startTime = 0;
        
        const startRecording = () => {
            document.getElementById('record-button').style.display = 'none';
            document.getElementById('stop-button').style.display = 'flex';
            document.getElementById('waveform-placeholder').style.display = 'flex';
            document.getElementById('timer').textContent = '00:00';
            
            // Start timer
            startTime = Date.now();
            timerInterval = setInterval(updateTimer, 1000);
            
            // Animation for waveform
            animateWaveform();
            
            navigator.mediaDevices.getUserMedia({ audio: true })
                .then(stream => {
                    mediaRecorder = new MediaRecorder(stream);
                    mediaRecorder.ondataavailable = event => {
                        audioChunks.push(event.data);
                    };
                    
                    mediaRecorder.onstop = () => {
                        audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
                        audioUrl = URL.createObjectURL(audioBlob);
                        
                        // Enable play button
                        document.getElementById('play-button').style.display = 'flex';
                        
                        // Enable the delete button
                        document.getElementById('delete-button').style.display = 'flex';
                        
                        // Show success message
                        document.getElementById('success-message').style.display = 'block';
                        
                        // Send data to Streamlit
                        const reader = new FileReader();
                        reader.readAsDataURL(audioBlob);
                        reader.onloadend = function() {
                            const base64data = reader.result.split(',')[1];
                            // Set the data in a hidden input that Streamlit can access
                            document.getElementById('audio-data').value = base64data;
                            // Trigger change event for Streamlit to detect
                            const event = new Event('change');
                            document.getElementById('audio-data').dispatchEvent(event);
                        };
                    };
                    
                    audioChunks = [];
                    mediaRecorder.start();
                    isRecording = true;
                })
                .catch(error => {
                    console.error('Error accessing microphone:', error);
                    document.getElementById('record-button').style.display = 'flex';
                    document.getElementById('stop-button').style.display = 'none';
                });
        };
        
        const stopRecording = () => {
            if (mediaRecorder && isRecording) {
                mediaRecorder.stop();
                isRecording = false;
                
                // Stop the timer
                clearInterval(timerInterval);
                
                // Update UI
                document.getElementById('record-button').style.display = 'flex';
                document.getElementById('stop-button').style.display = 'none';
            }
        };
        
        const playAudio = () => {
            if (audioUrl) {
                const audio = new Audio(audioUrl);
                audio.play();
            }
        };
        
        const deleteAudio = () => {
            audioChunks = [];
            audioBlob = null;
            if (audioUrl) {
                URL.revokeObjectURL(audioUrl);
                audioUrl = null;
            }
            
            // Reset UI
            document.getElementById('play-button').style.display = 'none';
            document.getElementById('delete-button').style.display = 'none';
            document.getElementById('waveform-placeholder').style.display = 'none';
            document.getElementById('success-message').style.display = 'none';
            document.getElementById('timer').textContent = '';
            
            // Clear hidden input
            document.getElementById('audio-data').value = '';
            const event = new Event('change');
            document.getElementById('audio-data').dispatchEvent(event);
        };
        
        const updateTimer = () => {
            const elapsedTime = Math.floor((Date.now() - startTime) / 1000);
            const minutes = Math.floor(elapsedTime / 60).toString().padStart(2, '0');
            const seconds = (elapsedTime % 60).toString().padStart(2, '0');
            document.getElementById('timer').textContent = `${minutes}:${seconds}`;
        };
        
        const animateWaveform = () => {
            const bars = document.querySelectorAll('.waveform-placeholder .bar');
            
            bars.forEach(bar => {
                const height = Math.floor(Math.random() * 30) + 5;
                bar.style.height = `${height}px`;
            });
            
            if (isRecording) {
                setTimeout(animateWaveform, 200);
            } else {
                // Reset bars
                bars.forEach(bar => {
                    bar.style.height = '20px';
                });
            }
        };
    </script>
    """
    
    # Custom HTML for audio recorder
    html_content = f"""
    <div class="custom-audio-recorder">
        <div class="audio-controls">
            <button id="record-button" class="audio-button" onclick="startRecording()">
                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3Z"></path>
                    <path d="M19 10v2a7 7 0 0 1-14 0v-2"></path>
                    <line x1="12" x2="12" y1="19" y2="22"></line>
                </svg>
            </button>
            
            <button id="stop-button" class="audio-button" onclick="stopRecording()" style="display: none;">
                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <rect width="6" height="6" x="9" y="9"></rect>
                </svg>
            </button>
            
            <button id="play-button" class="audio-button" onclick="playAudio()" style="display: none;">
                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <polygon points="5 3 19 12 5 21 5 3"></polygon>
                </svg>
            </button>
            
            <button id="delete-button" class="audio-button" onclick="deleteAudio()" style="display: none;">
                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M3 6h18"></path>
                    <path d="M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6"></path>
                    <path d="M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2"></path>
                </svg>
            </button>
            
            <div class="audio-waveform">
                <div id="waveform-placeholder" class="waveform-placeholder" style="display: none;">
                    {' '.join([f'<div class="bar" style="height: 20px;"></div>' for _ in range(30)])}
                </div>
                <span id="timer" class="timer"></span>
            </div>
        </div>
        
        <input type="hidden" id="audio-data" name="audio_data">
    </div>
    
    <div id="success-message" style="display: none; background-color: #e8f5e9; border-radius: 8px; padding: 12px; margin: 15px 0; border-left: 4px solid #4caf50;">
        <div style="display: flex; align-items: center;">
            <div style="background-color: #4caf50; width: 30px; height: 30px; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin-right: 12px;">
                <span style="color: white; font-size: 16px;">✓</span>
            </div>
            <div style="font-weight: 500; color: #2e7d32;">Audio recorded successfully!</div>
        </div>
    </div>
    
    {custom_js}
    """
    
    return html_content

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
    
    if 'audio_data' not in st.session_state:
        st.session_state.audio_data = None
    
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
            
            # Use custom audio recorder component
            recorder_html = custom_audio_recorder()
            audio_data = st.components.v1.html(recorder_html, height=180)
            
            # Get the audio data from the component via session state
            audio_data_input = st.empty()
            audio_data_base64 = audio_data_input.text_input("Hidden Audio Data", "", key="audio_data_input", label_visibility="collapsed")
            
            if audio_data_base64:
                # Convert base64 to audio file
                try:
                    audio_bytes = base64.b64decode(audio_data_base64)
                    audio_file = BytesIO(audio_bytes)
                    audio_file.name = "recorded_audio.wav"
                    st.session_state.audio_data = audio_file
                except Exception as e:
                    st.error(f"Error processing audio data: {str(e)}")
            
            if st.session_state.audio_data and st.button("Transcribe Recorded Audio", key="record_transcribe", use_container_width=True):
                # Attempt Transcription
                with st.spinner("Processing your audio..."):
                    success, result = transcribe_audio(st.session_state.audio_data)
                    
                    if success:
                        transcription_result = result
                    else:
                        st.error(result)

    # Display Transcription Result
    if transcription_result:
        # Create columns to control width for the transcription result
        res_col1, res_col2, res_col3 = st.columns([1, 3, 1])
        
        with res_col2:
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
                if st.button(" Copy to Clipboard", type="secondary"):
                    st.info("Text copied to clipboard functionality would be implemented here in a full app")
            
            with col2:
                # Download Button
                txt_filename = "transcription.txt"
                txt_bytes = BytesIO(transcription_result.encode("utf-8"))
                st.download_button(
                    label=" Download Transcription",
                    data=txt_bytes,
                    file_name=txt_filename,
                    mime="text/plain"
                )

if __name__ == "__main__":
    main()
