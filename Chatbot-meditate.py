from pydub import AudioSegment
from openai import OpenAI
import streamlit as st
import json
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
def text_to_speech(text, voice_type="alloy", api_key=None):
    try:
        client = OpenAI(api_key=api_key)
        response = client.audio.speech.create(model="tts-1", voice=voice_type, input=text)
        speech_file_path = "speech.mp3"
        response.stream_to_file(speech_file_path)
        return str(speech_file_path)
    except Exception as e:
        st.error(f"Error in text-to-speech conversion: {e}")
        return None

def generate_meditation_script(user_input, api_key):
    client = OpenAI(api_key=api_key)
    full_prompt_input = f"""
    Generate a customized meditation script for someone who is saying: {user_input}.
    Format the script as a JSON object with a "script" field containing an array, where each element represents a segment of the script.
    Each segment should have a "type" field indicating whether it's "speech" or "pause",
    and a "content" field containing the text for speech segments or the pause duration in seconds for pause segments.
    Only output the JSON object with a cumulative duration (including pauses) of around 30 seconds.

    Example format:
    {{
        "script": [
            {{
                "type": "speech",
                "content": "Welcome to your guided meditation."
            }},
            {{
                "type": "pause",
                "content": 2
            }},
            {{
                "type": "speech",
                "content": "Take a deep breath and relax."
            }}
        ]
    }}
    """
    messages = [{"role": "user", "content": full_prompt_input}]
    response = client.chat.completions.create(model="gpt-4-turbo",  response_format={ "type": "json_object" },  messages=messages, max_tokens=500)
    return response.choices[0].message.content.strip()

def combine_audio_segments(script, voice_type, api_key):
    audio_segments = []
    for segment in script:
        if segment["type"] == "speech":
            speech_file_path = text_to_speech(segment["content"], voice_type, api_key)
            if speech_file_path:
                audio_segments.append(AudioSegment.from_mp3(speech_file_path))
        elif segment["type"] == "pause":
            pause_duration = int(float(segment["content"]) * 1000)  # Convert seconds to milliseconds
            audio_segments.append(AudioSegment.silent(duration=pause_duration))

    combined = AudioSegment.empty()
    for segment in audio_segments:
        combined += segment

    combined_file_path = "combined_speech.mp3"
    combined.export(combined_file_path, format="mp3")
    return combined_file_path
with st.sidebar:
    openai_api_key = st.text_input("OpenAI API Key", key="tts_api_key", type="password")
    "[Get an OpenAI API key](https://platform.openai.com/account/api-keys)"
    "[View the source code](https://github.com/streamlit/llm-examples/blob/main/TextToSpeech.py)"
    "[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/streamlit/llm-examples?quickstart=1)"

st.title("🧘 MeditateGPT")
st.caption("🚀 Customized Meditation Sessions")

# Text input
user_input = st.text_area("How are you feeling right now:", height=150)

# Voice selection dropdown
voice_type = st.selectbox("Choose the voice:", ["alloy", "echo", "fable", "onyx", "nova", "shimmer"])

# Convert button
if st.button("Generate Meditation"):
    if not openai_api_key:
        st.info("Please add your OpenAI API key to continue.")
        st.stop()

    meditation_script_json = generate_meditation_script(user_input, openai_api_key)
    print("\n\n\n ", meditation_script_json, "\n\n\n")
    meditation_script = json.loads(meditation_script_json)["script"]

    combined_file_path = combine_audio_segments(meditation_script, voice_type, openai_api_key)
    if combined_file_path:
        # Display audio player and download link
        audio_file = open(combined_file_path, 'rb')
        audio_bytes = audio_file.read()
        st.audio(audio_bytes, format='audio/mp3')
        st.download_button(label="Download Meditation", data=audio_bytes, file_name="meditation.mp3", mime="audio/mp3")