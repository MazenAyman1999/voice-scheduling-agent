import utils
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
        - 👤: {meeting[utils.host_name_key]}
        - 📅: {meeting[utils.date_key]}
        - ⏰: {meeting[utils.time_key]}
        {f'- 🏷️: {meeting[utils.title_key]}' if meeting.get(utils.title_key) else ''}
        ⌛: {meeting[utils.duration_key]}
        - 🔗: [Event Link]({meeting[utils.link_key]})
        """)
else:
    st.sidebar.info("No meetings scheduled yet.")