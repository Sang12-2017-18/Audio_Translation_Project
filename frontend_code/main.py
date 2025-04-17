## This is the streamlit app.
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import streamlit as st

from helpers import translate_text, transcribe_audio, extract_audio

st.title("🎥 Video Translator App")

mode = st.radio("Select Input Mode", ["Upload audio file", "Use YouTube URL"])

# --- Mode 1: Upload and Transcribe ---
if mode == "Upload audio file":
    uploaded_file = st.file_uploader("Upload the audio file", type=["mp3", "wav", "m4a"])

    if uploaded_file and st.button("Transcribe and Translate"):
        with st.spinner("Transcribing..."):
            file_bytes = uploaded_file.read()
            result, error = transcribe_audio(file_bytes=file_bytes)
            if result:
                transcript = result["transcript"]
                st.text_area("📝 Transcript", transcript, height=150)
                with st.spinner("Translating..."):
                    translation_result, error = translate_text(transcript)
                    if translation_result:
                        st.text_area("🌍 Translation (English)", translation_result["translation"], height=150)
                    else:
                        st.error(f"Translation error: {error}")
            else:
                st.error(f"Transcription error: {error}")

# --- Mode 2: YouTube Download → Transcribe ---
elif mode == "Use YouTube URL":
    with st.form("video_input_form"):
        youtube_url = st.text_input("YouTube Video URL")
        start_time = st.number_input("Start Time (seconds)", min_value=0, value=0)
        end_time = st.number_input("End Time (seconds)", min_value=1, value=60)
        submitted = st.form_submit_button("Extract and Process")

    if submitted:
        with st.spinner("Extracting audio from YouTube..."):
            result, error = extract_audio(youtube_url, start_time, end_time)
            if result and result.get("success"):
                audio_file_path = result["audio_file"]
                st.audio(audio_file_path)
                st.success("Audio extracted!")

                with st.spinner("Transcribing..."):
                    result, error = transcribe_audio(audio_file_path=audio_file_path)
                    if result:
                        transcript = result["transcript"]
                        st.text_area("📝 Transcript", transcript, height=150)
                        with st.spinner("Translating..."):
                            translation_result, error = translate_text(transcript)
                            if translation_result:
                                st.text_area("🌍 Translation (English)", translation_result["translation"], height=150)
                            else:
                                st.error(f"Translation error: {error}")
                    else:
                        st.error(f"Transcription error: {error}")
            else:
                st.error(f"Error extracting audio: {error}")