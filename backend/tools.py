import utils
from typing import Optional
from urllib.parse import urlencode
from datetime import datetime, timedelta


def schedule_meeting(host_name: str, date: str, time: str, duration: str, title: Optional[str] = None) -> dict[str]:
    details = {utils.host_name_key: host_name, utils.date_key: date, utils.time_key: time, utils.duration_key: duration}
    start_timestamp = datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M")
    duration_hours, duration_minutes = map(int, duration.split(":"))
    end_timestamp = start_timestamp + timedelta(hours=duration_hours, minutes=duration_minutes)
    if title is not None:
        details[utils.title] = title
    details[utils.link_key] = "https://www.google.com/calendar/render?" + urlencode({
        "action": "TEMPLATE",
        "description": f"Meeting Host Name: {host_name}\nMeeting Title: {str(details.get(utils.title_key))})",
        "dates": f"{start_timestamp.strftime('%Y%m%dT%H%M%S')}/{end_timestamp.strftime('%Y%m%dT%H%M%S')}",
    })
    return details