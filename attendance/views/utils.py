import datetime
from typing import Optional

from django.db.models import Count

from attendance.models import GosGradeLevel, GosPreseasonCrew, GosProgram, GosSubteam


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
