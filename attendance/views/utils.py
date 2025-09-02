import datetime
from typing import Optional, Dict, List

from django.db.models import Count

from attendance.models import GosGradeLevel, GosPreseasonCrew, GosProgram, GosSubteam
from attendance.models.date_ranges import get_date_range


class CalendarEvent:
    def __init__(
        self,
        time_in: datetime.datetime,
        time_out: Optional[datetime.datetime],
        title: str,
        color: Optional[str] = None,
        show_as_all_day: bool = False,
    ):
        self.time_in = time_in
        self.time_out = time_out
        self.title = title
        self.color = color
        self.show_as_all_day = show_as_all_day

    def __repr__(self):  # pragma: no cover
        return f"CalendarEvent - {type(self.time_in)}"


def create_calendar_events_from_attendance(query_set, title, color=None):
    visits = query_set.values("time_in__date").annotate(xyz=Count("time_in__date"))

    calendar_events = []
    for att in visits:
        calendar_events.append(
            CalendarEvent(
                time_in=datetime.datetime.fromisoformat(
                    att["time_in__date"].isoformat()
                ),
                time_out=None,
                title=f"{att['xyz']} " + title,
                color=color,
                show_as_all_day=True,
            )
        )

    return calendar_events


def get_navbar_context():
    context = {}
    context["NAVBAR_GOS_CREWS"] = GosPreseasonCrew.choices
    context["NAVBAR_GOS_PROGRAMS"] = GosProgram.choices
    context["NAVBAR_GOS_SUBTEAMS"] = GosSubteam.choices
    context["NAVBAR_GOS_GRADES"] = GosGradeLevel.choices

    return context


def get_weeks_since_start() -> int:
    start_time, end_time = get_date_range()
    print(start_time, end_time)
    delta = end_time - start_time
    num_weeks = delta.days // 7
    print(delta, num_weeks)
    return num_weeks


def get_recommended_hour_lines() -> List[Dict]:
    num_weeks = get_weeks_since_start()

    return [
        dict(
            y=8 * num_weeks,
            line_width=2,
            line_dash="dash",
            line_color="green",
            annotation_text="8hr/week",
        ),
        dict(
            y=6 * num_weeks,
            line_width=2,
            line_color="green",
            annotation_text="6hr/week",
        ),
        dict(
            y=3 * num_weeks, line_width=2, line_color="gold", annotation_text="3hr/week"
        ),
        dict(
            y=1 * num_weeks, line_width=2, line_color="red", annotation_text="1hr/week"
        ),
    ]


def get_recommended_hour_series():
    num_weeks = get_weeks_since_start()

    dates = []

    start_date, _ = get_date_range()

    for i in range(num_weeks + 1):
        dates.append(start_date + datetime.timedelta(i * 7))

    return [
        dates,
        ("8hrs/week", [i * 8 for i in range(num_weeks + 1)]),
        ("6hrs/week", [i * 6 for i in range(num_weeks + 1)]),
        ("3hrs/week", [i * 3 for i in range(num_weeks + 1)]),
        ("1hrs/week", [i * 1 for i in range(num_weeks + 1)]),
    ]
