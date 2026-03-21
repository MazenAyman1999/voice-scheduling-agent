from enum import Enum


class MeetingDetails(Enum):
    host_name = "host_name"
    date = "date"
    time = "time"
    duration = "duration"
    title = "title"
    link = "link"
host_name_key = MeetingDetails.host_name.value
date_key = MeetingDetails.date.value
time_key = MeetingDetails.time.value
duration_key = MeetingDetails.duration.value
title_key = MeetingDetails.title.value
link_key = MeetingDetails.link.value