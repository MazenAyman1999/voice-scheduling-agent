import streamlit as st
from typing import Optional
from datetime import datetime
from googleapiclient.discovery import build



def schedule_meeting(host_name: str, date: str, time: str, title: Optional[str] = None) -> dict[str]:
    # details = {"host_name": host_name, "date": date, "time": time}
    # if title is not None:
    #     details["title"] = title
    # return details
    
    dt_str = f"{date} {time}"
    start_dt = datetime.strptime(dt_str, "%Y-%m-%d %H:%M")

    end_dt = start_dt.replace(hour=start_dt.hour + 1)

    # Authenticate
    creds = st.session_state.get("credentials")

    service = build("calendar", "v3", credentials=creds)

    event = {
        "summary": title if title else f"Meeting with {host_name}",
        "start": {
            "dateTime": start_dt.isoformat(),
            "timeZone": "Africa/Cairo",
        },
        "end": {
            "dateTime": end_dt.isoformat(),
            "timeZone": "Africa/Cairo",
        },
    }

    created_event = service.events().insert(
        calendarId="primary",
        body=event
    ).execute()

    return {
        "host_name": host_name,
        "date": date,
        "time": time,
        "title": title,
        "link": created_event.get("htmlLink")
    }