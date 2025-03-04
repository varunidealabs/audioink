def transcribe_page():
    # Add custom CSS for the new design
    st.markdown("""
    <style>
    .input-method-container {
        display: flex;
        justify-content: center;
        gap: 20px;
        margin-bottom: 20px;
    }
    .input-method-button {
        padding: 12px 24px;
        border: 2px solid #e0e4eb;
        border-radius: 10px;
        background-color: #f8f9fa;
        color: #2c3e50;
        cursor: pointer;
        transition: all 0.3s ease;
        text-align: center;
        min-width: 180px;
        font-weight: bold;
    }
    .input-method-button:hover {
        background-color: #ff5722;
        color: white;
        border-color: #ff5722;
    }
    .input-method-button.active {
        background-color: #ff5722;
        color: white;
        border-color: #ff5722;
    }
    .transcribe-content {
        margin-top: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

    # Add JavaScript for interactivity
    st.markdown("""
    <script>
    document.addEventListener('DOMContentLoaded', function() {
        const uploadButton = document.getElementById('upload-button');
        const recordButton = document.getElementById('record-button');
        const uploadContent = document.getElementById('upload-content');
        const recordContent = document.getElementById('record-content');
        
        uploadButton.addEventListener('click', function() {
            uploadButton.classList.add('active');
            recordButton.classList.remove('active');
            uploadContent.style.display = 'block';
            recordContent.style.display = 'none';
        });
        
        recordButton.addEventListener('click', function() {
            recordButton.classList.add('active');
            uploadButton.classList.remove('active');
            recordContent.style.display = 'block';
            uploadContent.style.display = 'none';
        });
        
        // Default to upload method
        uploadButton.classList.add('active');
        recordContent.style.display = 'none';
    });
    </script>
    """, unsafe_allow_html=True)

    st.markdown('<div class="transcribe-container">', unsafe_allow_html=True)
    st.header("🎙️ Transcribe Your Audio")
    
    # Input Method Selection
    st.markdown('''
    <div class="input-method-container">
        <div id="upload-button" class="input-method-button">
            Upload Audio
        </div>
        <div id="record-button" class="input-method-button">
            Record Audio
        </div>
    </div>
    ''', unsafe_allow_html=True)
    
    # Upload Audio Content
    st.markdown('<div id="upload-content" class="transcribe-content">', unsafe_allow_html=True)
    st.subheader("Upload Audio File")
    uploaded_file = st.file_uploader("Choose an audio file", type=SUPPORTED_FORMATS)
    
    transcription_text = None  # Store the transcribed text
    
    if uploaded_file:
        valid, message = validate_file(uploaded_file)
        if not valid:
            st.error(message)
        elif st.button("⚡ Transcribe Uploaded Audio"):
            processed_file = convert_to_wav(uploaded_file)
            if processed_file:
                success, result = transcribe_audio(processed_file)
                if success:
                    transcription_text = result
                    st.subheader("Transcription Result")
                    st.write(transcription_text)
                else:
                    st.error(result)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Record Audio Content
    st.markdown('<div id="record-content" class="transcribe-content" style="display:none;">', unsafe_allow_html=True)
    st.subheader("Record Audio")
    audio_data = st.audio_input("Record your audio")
    
    if audio_data:
        st.success("🎙️ Audio recorded successfully!")
        if st.button("⚡ Transcribe Recorded Audio"):
            audio_data.seek(0)
            success, result = transcribe_audio(audio_data)
            if success:
                transcription_text = result
                st.subheader("Transcription Result")
                st.write(transcription_text)
            else:
                st.error(result)
    st.markdown('</div>', unsafe_allow_html=True)

    # Download Button
    if transcription_text:
        txt_filename = "transcription.txt"
        txt_bytes = BytesIO(transcription_text.encode("utf-8"))
        st.download_button(
            label="⬇️ Download as TXT",
            data=txt_bytes,
            file_name=txt_filename,
            mime="text/plain"
        )
    
    st.markdown('</div>', unsafe_allow_html=True)
