import cohere
import json
import tempfile
import streamlit as st
import speech_recognition as sr
from typing import Optional
from gtts import gTTS


cohere_client = cohere.ClientV2(st.secrets["COHERE_API_KEY"], log_warning_experimental_features=False)

system_prompt = """
You are a meeting scheduling assistant.
You don't discuss or do any other task.
You start the conversation by asking for the following:
- Ask for the meeting's host name.
- Ask for the meeting's date.
- Ask for the meeting's time.
- Ask for the meeting's title (optionally).
Then, you confirm the meeting details with the user.
IMPORTANT:
- Only after you confirm the meeting details with the user, return the meeting details in JSON format.
- Don't ever tell the user that you'll return in JSON format.
"""

def get_meeting_details(host_name: str, date: str, time: str, title: Optional[str] = None) -> dict[str]:
    details = {"host_name": host_name, "date": date, "time": time}
    if title is not None:
        details["title"] = title
    return details

tools_map = {"get_meeting_details": get_meeting_details}

tools = [
    {
        "type": "function",
        "function": {
            "name": "get_meeting_details",
            "description": "Writes a meeting's details in JSON format.",
            "parameters": {
                "type": "object",
                "properties": {
                    "host_name": {
                        "type": "string",
                        "description": "The name of the meeting host.",
                    },
                    "date": {
                        "type": "string",
                        "format": "date",
                        "description": "The date of the meeting.",
                    },
                    "time": {
                        "type": "string",
                        "format": "time",
                        "description": "The time of the meeting.",
                    },
                    "title": {
                        "type": "string",
                        "description": "The title of the meeting.",
                    }
                },
                "required": ["host_name", "date", "time"]
            }
        }
    }
]

if "conversation" not in st.session_state:
    st.session_state.conversation = [{"role": "system", "content": system_prompt}]
if "messages" not in st.session_state:
    st.session_state.messages = []
st.title("📅 Meeting Scheduler Assistant")
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
input = st.chat_input(placeholder = "Type your message or click the mic button to speak ...", accept_audio= True)
if input:
    if input.audio:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as f:
            f.write(input.audio.read())
            audio_path = f.name
        recognizer = sr.Recognizer()
        with sr.AudioFile(audio_path) as source:
            audio_data = recognizer.record(source)
        try:
            user_prompt = recognizer.recognize_google(audio_data)
        except sr.UnknownValueError:
            st.error("Could not understand audio")
            user_prompt = None
    st.session_state.conversation.append(({"role": "user", "content": user_prompt}))
    st.session_state.messages.append(("You", user_prompt))
    with st.chat_message("user"):
        st.markdown(user_prompt)
    with st.spinner("Thinking..."):
        response_obj = cohere_client.chat(model="command-a-03-2025", messages=st.session_state.conversation, tools=tools,
                                          temperature=0.3)
        if response_obj.message.tool_calls:
            for tc in response_obj.message.tool_calls:
                if (tc.function.name == "get_meeting_details"):
                    meeting_details = tools_map[tc.function.name](**json.loads(tc.function.arguments))
                    response = f"Meeting scheduled! Link "
                    st.session_state.history.append(("Agent", f"Meeting scheduled! Link "))
        else:
            response = response_obj.message.content[0].text
            st.session_state.conversation.append(({"role": "assistant", "content": response}))
            st.session_state.messages.append(("Agent", response))
        tts = gTTS(response)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as f:
            tts.save(f.name)
            st.audio(f.name, format="audio/mp3", autoplay=True)
        with st.chat_message("assistant"):
            st.markdown(response)