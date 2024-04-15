from pathlib import Path
from pydub import AudioSegment
from openai import OpenAI
import streamlit as st

def text_to_speech(text, voice_type="alloy", api_key=None):
    max_length = 4096
    chunks = [text[i:i + max_length] for i in range(0, len(text), max_length)]
    audio_files = []

    for i, chunk in enumerate(chunks):
        try:
            client = OpenAI(api_key=api_key)
            response = client.audio.speech.create(model="tts-1",
                                                  voice=voice_type,
                                                  input=chunk)
            speech_file_path = Path(f"chunk_{i}.mp3")
            response.stream_to_file(speech_file_path)
            audio_files.append(AudioSegment.from_mp3(speech_file_path))
        except Exception as e:
            st.error(f"Error in text-to-speech conversion for chunk {i}: {e}")
            return None

    # Combine audio files into one
    combined = AudioSegment.empty()
    for audio in audio_files:
        combined += audio

    # Export combined audio to a file
    combined_file_path = "combined_speech.mp3"
    combined.export(combined_file_path, format="mp3")
    return combined_file_path

with st.sidebar:
    openai_api_key = st.text_input("OpenAI API Key", key="tts_api_key", type="password")
    "[Get an OpenAI API key](https://platform.openai.com/account/api-keys)"
    "[View the source code](https://github.com/streamlit/llm-examples/blob/main/TextToSpeech.py)"
    "[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/streamlit/llm-examples?quickstart=1)"

st.title("🎙️ Text to Speech Converter")
st.caption("🚀 A Streamlit app for converting text to speech using OpenAI")

# Text input
user_input = st.text_area("Enter the text you want to convert to speech:", height=150)

# Voice selection dropdown
voice_type = st.selectbox(
    "Choose the voice:",
    ["alloy", "echo", "fable", "onyx", "nova", "shimmer"])

# Convert button
if st.button("Convert to Speech"):
    if not openai_api_key:
        st.info("Please add your OpenAI API key to continue.")
        st.stop()

    speech_file_path = text_to_speech(user_input, voice_type, openai_api_key)
    if speech_file_path:
        # Display audio player and download link
        audio_file = open(speech_file_path, 'rb')
        audio_bytes = audio_file.read()
        st.audio(audio_bytes, format='audio/mp3')
        st.download_button(label="Download Speech",
                           data=audio_bytes,
                           file_name="speech.mp3",
                           mime="audio/mp3")