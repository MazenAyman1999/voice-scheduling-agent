from typing import Optional
from urllib.parse import urlencode
from datetime import datetime, timedelta
from backend import utils


def schedule_meeting(host_name: str, date: str, time: str, duration: str, title: Optional[str] = None) -> dict[str]:
    """
    Creates a meeting record and generate a Google Calendar event link.
    Args:
        host_name (str): Name of the meeting host.
        date (str): Meeting date in 'YYYY-MM-DD' format.
        time (str): Meeting time in 'HH:MM' format (24-hour).
        duration (str): Duration in 'HH:MM' format.
        title (Optional[str]): Optional meeting title.
    Returns:
        dict[str]: Dictionary containing meeting details:
            - host_name
            - date
            - time
            - duration
            - title (optional)
            - link (Google Calendar event link)
    Notes:
        - Computes start and end timestamps based on date, time, and duration.
        - Generates a Google Calendar "TEMPLATE" link for quick event creation.
    """
    details = {utils.host_name_key: host_name, utils.date_key: date, utils.time_key: time, utils.duration_key: duration}
    start_timestamp = datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M")
    duration_hours, duration_minutes = map(int, duration.split(":"))
    end_timestamp = start_timestamp + timedelta(hours=duration_hours, minutes=duration_minutes)
    if title is not None:
        details[utils.title_key] = title
    details[utils.link_key] = "https://www.google.com/calendar/render?" + urlencode({
        "action": "TEMPLATE",
        "details": f"Meeting Host Name: {host_name}\nMeeting Title: {str(details.get(utils.title_key))}",
        "dates": f"{start_timestamp.strftime('%Y%m%dT%H%M%S')}/{end_timestamp.strftime('%Y%m%dT%H%M%S')}",
    })
    return details