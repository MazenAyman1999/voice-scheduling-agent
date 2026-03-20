# import cohere
# import json
# import tempfile
# import streamlit as st
# import speech_recognition as sr
# from typing import Optional
# from gtts import gTTS


# cohere_client = cohere.ClientV2(st.secrets["COHERE_API_KEY"], log_warning_experimental_features=False)

# system_prompt = """
# You are a strict meeting scheduling assistant.
# You do not engage in any conversation outside of scheduling meetings.
# Your flow MUST follow these steps:
#     1) Start by asking for:
#         - Host name
#         - Meeting date
#         - Meeting time
#         - Meeting title (OPTIONAL — user may skip it)
#     2) Validate inputs before proceeding:
#         - Host name must be a non-empty string.
#         - Date MUST include day, month, and YEAR (e.g., 25 March 2026 or 2026-03-25).
#         - Title is optional.
#     3) Handle missing or invalid inputs:
#         - If any required field is missing or unclear, ask ONLY for the missing/invalid field.
#         - Do NOT restart the whole process.
#         - If the date is missing the year, explicitly ask the user to include the year.
#         - If the title is missing, proceed without forcing it.
#     4) Confirmation step:
#         - Once all required details are collected, present a clear summary:
#             Host Name:
#             Date:
#             Time:
#             Title: (show None if not provided)
#         - Ask the user for confirmation (yes/no or explicit approval).
#     5) Scheduling rule (CRITICAL):
#         - ONLY schedule the meeting AFTER the user explicitly confirms the details.
#         - Do NOT assume confirmation.
#     6) Behavior constraints:
#         - Be concise and structured.
#         - Do NOT auto-correct without asking the user.
#         - Do NOT perform any task other than meeting scheduling.
#     7) Edge cases:
#         - If the user provides multiple values (e.g., two dates), ask for clarification.
#         - If the user changes a field after confirmation, restart confirmation with updated values.
#         - If the user provides all details in one message, skip questions and go directly to validation + confirmation.
#     8) Audio handling:
#         - If the user input is unclear, ask them to repeat what was said.
# """

# def schedule_meeting(host_name: str, date: str, time: str, title: Optional[str] = None) -> dict[str]:
#     details = {"host_name": host_name, "date": date, "time": time}
#     if title is not None:
#         details["title"] = title
#     return details

# tools_map = {"schedule_meeting": schedule_meeting}

# tools = [
#     {
#         "type": "function",
#         "function": {
#             "name": "schedule_meeting",
#             "description": "Schedules a meeting on Google Calender.",
#             "parameters": {
#                 "type": "object",
#                 "properties": {
#                     "host_name": {
#                         "type": "string",
#                         "description": "The name of the meeting host.",
#                     },
#                     "date": {
#                         "type": "string",
#                         "format": "date",
#                         "description": "The date of the meeting.",
#                     },
#                     "time": {
#                         "type": "string",
#                         "format": "time",
#                         "description": "The time of the meeting.",
#                     },
#                     "title": {
#                         "type": "string",
#                         "description": "The title of the meeting.",
#                     }
#                 },
#                 "required": ["host_name", "date", "time"]
#             }
#         }
#     }
# ]

# if "conversation" not in st.session_state:
#     st.session_state.conversation = [{"role": "system", "content": system_prompt}]
# if "messages" not in st.session_state:
#     st.session_state.messages = []
# if "meetings" not in st.session_state:
#     st.session_state.meetings = []
# st.title("Voice Scheduling Agent")
# for msg in st.session_state.messages:
#     with st.chat_message(msg["role"]):
#         st.markdown(msg["content"])
# input = st.chat_input(placeholder = "Type your message or click the mic button to speak ...", accept_audio= True)
# user_prompt = None
# if input:
#     if input.audio:
#         with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as f:
#             f.write(input.audio.read())
#             audio_path = f.name
#         recognizer = sr.Recognizer()
#         with sr.AudioFile(audio_path) as source:
#             audio_data = recognizer.record(source)
#         try:
#             user_prompt = recognizer.recognize_google(audio_data)
#         except sr.UnknownValueError:
#             unclear_msg = "[Unclear audio]"
#             user_prompt = unclear_msg
#     elif input.text:
#         user_prompt = input.text
#     if user_prompt:
#         st.session_state.conversation.append({"role": "user", "content": user_prompt})
#         st.session_state.messages.append({"role": "user", "content": user_prompt})
#         with st.chat_message("user"):
#             st.markdown(user_prompt)
#     with st.spinner("Thinking..."):
#         response = cohere_client.chat(model="command-a-03-2025", messages=st.session_state.conversation, tools=tools,
#                                       temperature=0.3)
#         if response.message.tool_calls:
#             for tc in response.message.tool_calls:
#                 if (tc.function.name == "schedule_meeting"):
#                     meeting_details = tools_map[tc.function.name](**json.loads(tc.function.arguments))
#                     st.session_state.meetings.append(meeting_details)
#                     title_line = f'Title: {meeting_details["title"]}' if meeting_details.get("title") else ""
#                     assistant_msg = f"""
#                     A meeting was scheduled successfully with the following details:\n
#                     Host Name: {meeting_details["host_name"]}\n
#                     Date: {meeting_details["date"]}\n
#                     Time: {meeting_details["time"]}\n
#                     {title_line}"""
#         else:
#             assistant_msg = response.message.content[0].text
#         st.session_state.conversation.append({"role": "assistant", "content": assistant_msg})
#         st.session_state.messages.append({"role": "assistant", "content": assistant_msg})
#         tts = gTTS(assistant_msg)
#         with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as f:
#             tts.save(f.name)
#             st.audio(f.name, format="audio/mp3", autoplay=True)
#         with st.chat_message("assistant"):
#             st.markdown(assistant_msg)
# st.sidebar.title("📌 Scheduled Meetings")
# if st.session_state.meetings:
#     for i, meeting in enumerate(st.session_state.meetings, 1):
#         st.sidebar.markdown(f"""
#         **Meeting {i}**
#         - 👤: {meeting["host_name"]}
#         - 📅: {meeting["date"]}
#         - ⏰: {meeting["time"]}
#         {f'- 🏷️: {meeting["title"]}' if meeting.get("title") else ''}
#         """)
# else:
#     st.sidebar.info("No meetings scheduled yet.")

import streamlit as st
from backend.llm import system_prompt, chat
from backend.audio import speech_to_text, text_to_speech


st.title("Voice Scheduling Agent")
if "conversation" not in st.session_state:
    st.session_state.conversation = [{"role": "system", "content": system_prompt}]
if "meetings" not in st.session_state:
    st.session_state.meetings = []
for msg in st.session_state.conversation[1:]:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
input = st.chat_input(placeholder="Type or speak ...", accept_audio=True)
if input:
    if input.audio:
        user_prompt = speech_to_text(input.audio)
    else:
        user_prompt = input.text
    if user_prompt:
        st.session_state.conversation.append({"role": "user", "content": user_prompt})
        with st.chat_message("user"):
            st.markdown(user_prompt)
        with st.spinner("Thinking..."):
            assistant_msg, meeting = chat(st.session_state.conversation)
            if meeting:
                st.session_state.meetings.append(meeting)
            st.session_state.conversation.append({"role": "assistant", "content": assistant_msg})
            audio_path = text_to_speech(assistant_msg)
            st.audio(audio_path, autoplay=True)
            with st.chat_message("assistant"):
                st.markdown(assistant_msg)
st.sidebar.title("📌 Scheduled Meetings")
if st.session_state.meetings:
    for i, meeting in enumerate(st.session_state.meetings, 1):
        st.sidebar.markdown(f"""
        **Meeting {i}**
        - 👤: {meeting["host_name"]}
        - 📅: {meeting["date"]}
        - ⏰: {meeting["time"]}
        {f'- 🏷️: {meeting["title"]}' if meeting.get("title") else ''}
        """)
else:
    st.sidebar.info("No meetings scheduled yet.")