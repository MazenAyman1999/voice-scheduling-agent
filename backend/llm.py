import json
import cohere
import streamlit as st
from backend.tools import schedule_meeting
from backend import utils


cohere_client = cohere.ClientV2(st.secrets["COHERE_API_KEY"], log_warning_experimental_features=False)

system_prompt = """
You are a strict meeting scheduling assistant.
You do not engage in any conversation outside of scheduling meetings.
Your flow MUST follow these steps:
    1) Start by asking for:
        - Host name
        - Meeting date
        - Meeting time
        - Meeting Duration
        - Meeting title (OPTIONAL — user may skip it)
    2) Validate inputs before proceeding:
        - Host name must be a non-empty string.
        - Date MUST include day, month, and YEAR (e.g., 25 March 2026 or 2026-03-25).
        - Title is optional.
    3) Handle missing or invalid inputs:
        - If any required field is missing or unclear, ask ONLY for the missing/invalid field, don't ask for the whole details.
        - If the date is missing the year, explicitly ask the user to include the year.
        - If the title is missing, proceed without forcing it.
    4) Confirmation from the user:
        - Once all required details are collected, always before scheduling the meeting, present a clear summary:
            Host Name:
            Date:
            Time:
            Duration:
            Title: (show None if not provided)
        - Ask the user for confirmation.
        - ONLY schedule the meeting AFTER the user explicitly confirms the details.
        - Do NOT assume confirmation.
    5) Behavior constraints:
        - Be concise and structured.
        - Do NOT auto-correct without asking the user.
        - After scheduling a meeting, don't show the meeting link to the user.
    6) Edge cases:
        - If the user provides multiple values (e.g., two dates), ask for clarification.
        - If the user changes a field after confirmation, restart confirmation with updated values.
    7) Audio handling:
        - If the user input is unclear, ask them to repeat what was said.
"""

tools = [
    {
        "type": "function",
        "function": {
            "name": "schedule_meeting",
            "description": "Schedules a meeting only after user confirmation on the meeting details.",
            "parameters": {
                "type": "object",
                "properties": {
                    utils.host_name_key: {
                        "type": "string",
                        "description": "The name of the meeting host.",
                    },
                    utils.date_key: {
                        "type": "string",
                        "format": "date",
                        "description": "The date of the meeting in 'YYYY-MM-DD' format.",
                    },
                    utils.time_key: {
                        "type": "string",
                        "format": "time",
                        "description": "The time of the meeting in 'HH:MM' format.",
                    },
                    utils.duration_key: {
                        "type": "string",
                        "format": "time",
                        "description": "The duration of the meeting in hours and minutes only.",
                    },
                    utils.title_key: {
                        "type": "string",
                        "description": "The title of the meeting.",
                    }
                },
                "required": [utils.host_name_key, utils.date_key, utils.time_key, utils.duration_key]
            }
        }
    }
]

tools_map = {"schedule_meeting": schedule_meeting}

def chat(conversation: list[dict]) -> tuple:
    """
    Send conversation to a Cohere's LLM and handle tool execution if triggered.
    Args:
        conversation (list[dict]): Chat history including system, user, and assistant messages.
    Returns:
        tuple:
            - str: Assistant response text
            - dict | None: Meeting details if a meeting was scheduled, otherwise None
    Workflow:
        1. Send conversation to the LLM.
        2. Check if a tool call is requested.
        3. If tool call exists:
            - Execute the corresponding backend function.
            - Append tool response to conversation.
            - Call LLM again to generate final response.
        4. Return assistant reply and optional meeting data.
    """
    response = cohere_client.chat(model="command-a-03-2025", messages=conversation, tools=tools, temperature=0.3)
    if response.message.tool_calls:
        conversation.append(response.message)
        for tc in response.message.tool_calls:
            if (tc.function.name == "schedule_meeting"):
                meeting_details = tools_map[tc.function.name](**json.loads(tc.function.arguments))
                conversation.append(
                    {
                        "role": "tool",
                        "tool_call_id": tc.id,
                        "content": str(meeting_details),
                    }
                )
                return cohere_client.chat(model="command-a-03-2025", messages=conversation, tools=tools,
                                          temperature=0.3).message.content[0].text, meeting_details
    return response.message.content[0].text, None