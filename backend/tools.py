from typing import Optional
from urllib.parse import urlencode


def schedule_meeting(host_name: str, date: str, time: str, title: Optional[str] = None) -> dict[str]:
    details = {"host_name": host_name, "date": date, "time": time}
    if title is not None:
        details["title"] = title
    details["link"] = "https://www.google.com/calendar/render?" + urlencode({
        "action": "TEMPLATE",
        "text": details.get("title") or f"Meeting with {host_name}",
        "dates": f"{date.replace('-','')}T{time.replace(':','')}00/{date.replace('-','')}T{time.replace(':','')}00",
        "details": "Scheduled via Streamlit Voice Agent"
    })
    return details