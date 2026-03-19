import cohere
import json
import os
from dotenv import load_dotenv
from pydantic import BaseModel
from typing import Optional
from fastapi import FastAPI


app = FastAPI()

load_dotenv()

cohere_client = cohere.ClientV2(os.getenv("COHERE_API_KEY"), log_warning_experimental_features=False)

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
conversation = [{"role": "system", "content": system_prompt}]

def get_meeting_details(host_name: str, date: str, time: str, title: Optional[str] = None) -> str:
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

class ChatRequest(BaseModel):
    user_prompt: str

@app.post("/chat")
def chat(request: ChatRequest):
    global conversation
    conversation.append({"role": "user", "content": request.user_prompt})
    response_obj = cohere.chat(model="command-a-03-2025", messages=conversation, tools=tools, temperature=0.3)
    if response_obj.message.tool_calls:
        for tc in response_obj.message.tool_calls:
            if (tc.function.name == "get_meeting_details"):
                meeting_details = tools_map[tc.function.name](**json.loads(tc.function.arguments))
                conversation = [system_prompt]
                return {"response": f"Meeting scheduled! Link "}
    response = response_obj.message.content[0].text
    conversation.append({"role": "assistant", "content": response})
    return {"response": response}

# def main():
#     # global conversation
#     while True:
#         conversation.append({"role": "user", "content": input("User: ")})
#         response_obj = cohere_client.chat(model="command-a-03-2025", messages=conversation, tools=tools, temperature=0.3)
#         if response_obj.message.tool_calls:
#             for tc in response_obj.message.tool_calls:
#                 if (tc.function.name == "get_meeting_details"):
#                     meeting_details = tools_map[tc.function.name](**json.loads(tc.function.arguments))
#                     print(meeting_details)
#                     return
#         response = response_obj.message.content[0].text
#         conversation.append({"role": "assistant", "content": response})
#         print(f"Assistant: {response}")