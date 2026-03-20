import json
import streamlit as st
import cohere
from backend.tools import schedule_meeting


cohere_client = cohere.ClientV2(st.secrets["cohere"]["api_key"], log_warning_experimental_features=False)

system_prompt = """
You are a strict meeting scheduling assistant.
You do not engage in any conversation outside of scheduling meetings.
Your flow MUST follow these steps:
    1) Start by asking for:
        - Host name
        - Meeting date
        - Meeting time
        - Meeting title (OPTIONAL — user may skip it)
    2) Validate inputs before proceeding:
        - Host name must be a non-empty string.
        - Date MUST include day, month, and YEAR (e.g., 25 March 2026 or 2026-03-25).
        - Title is optional.
    3) Handle missing or invalid inputs:
        - If any required field is missing or unclear, ask ONLY for the missing/invalid field.
        - Do NOT restart the whole process.
        - If the date is missing the year, explicitly ask the user to include the year.
        - If the title is missing, proceed without forcing it.
    4) Confirmation step:
        - Once all required details are collected, before scheduling the meeting, present a clear summary:
            Host Name:
            Date:
            Time:
            Title: (show None if not provided)
        - Ask the user for confirmation.
    5) Scheduling rule (CRITICAL):
        - ONLY schedule the meeting AFTER the user explicitly confirms the details.
        - Do NOT assume confirmation.
    6) Behavior constraints:
        - Be concise and structured.
        - Do NOT auto-correct without asking the user.
        - Do NOT perform any task other than meeting scheduling.
    7) Edge cases:
        - If the user provides multiple values (e.g., two dates), ask for clarification.
        - If the user changes a field after confirmation, restart confirmation with updated values.
        - If the user provides all details in one message, skip questions and go directly to validation + confirmation.
    8) Audio handling:
        - If the user input is unclear, ask them to repeat what was said.
"""

tools = [
    {
        "type": "function",
        "function": {
            "name": "schedule_meeting",
            "description": "Schedules a meeting on Google Calender.",
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
                        "description": "The time of the meeting in hours and minutes only.",
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

tools_map = {"schedule_meeting": schedule_meeting}

def chat(conversation: list[dict]) -> tuple:
    response = cohere_client.chat(model="command-a-03-2025", messages=conversation, tools=tools, temperature=0.3)
    if response.message.tool_calls:
            for tc in response.message.tool_calls:
                if (tc.function.name == "schedule_meeting"):
                    meeting_details = tools_map[tc.function.name](**json.loads(tc.function.arguments))
                    return f"""
                    A meeting was scheduled successfully with the following details:\n
                    Host Name: {meeting_details['host_name']}\n
                    Date: {meeting_details['date']}\n
                    Time: {meeting_details['time']}\n
                    Title: { meeting_details.get("title", "None")}
                    Link: {meeting_details["link"]}
                    """, meeting_details
    return response.message.content[0].text, None