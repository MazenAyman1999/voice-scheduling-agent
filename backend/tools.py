from typing import Optional


def schedule_meeting(host_name: str, date: str, time: str, title: Optional[str] = None) -> dict[str]:
    details = {"host_name": host_name, "date": date, "time": time}
    if title is not None:
        details["title"] = title
    return details