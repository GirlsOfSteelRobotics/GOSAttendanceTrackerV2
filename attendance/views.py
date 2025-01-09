import datetime
from typing import Optional

from django.db.models import Count
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.views import generic

from attendance.models import GosStudent, GosAttendance

class IndexView(generic.TemplateView):
    template_name = "attendance/index.html"

    def get_context_data(self, **kwargs):
        calendar_events = []

        calendar_events.extend(
            create_calendar_events_from_attendance(GosAttendance, "GOS", "blue")
        )

        context = super().get_context_data(**kwargs)
        context["calendar_events"] = calendar_events
        return context


class GosStudentSummaryView(generic.ListView):
    model = GosStudent


class GosStudentDetailView(generic.DetailView):
    model = GosStudent
    slug_url_kwarg = "rfid"
    slug_field = "rfid"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["attendance"] = []
        return context


def gos_signin(request):
    return render(request, "attendance/gosattendance_signin.html")


def gos_log_attendance_rfid(request):
    rfid = request.POST["rfid"]
    students = GosStudent.objects.filter(rfid=rfid)
    if not students:
        return __login_failure_redirect(
            request, f"Invalid rfid name {rfid}", "attendance/gosattendance_signin.html"
        )

    return __gos_handle_login(request, students[0])


def gos_log_attendance_name(request):
    full_name = request.POST["full_name"].strip()
    name_parts = full_name.split(" ")
    if len(name_parts) != 2:
        return __login_failure_redirect(
            request,
            f"Invalid student name {full_name}, could not split the name into two parts",
            "attendance/gosattendance_signin.html",
        )

    first_name, last_name = name_parts
    students = GosStudent.objects.filter(first_name=first_name, last_name=last_name)
    if not students:
        return __login_failure_redirect(
            request,
            f"Invalid student name {full_name}",
            "attendance/gosattendance_signin.html",
        )

    return __gos_handle_login(request, students[0])


def __login_failure_redirect(request, error_msg, template_name):
    request.session["result_msg"] = error_msg
    request.session["good_result"] = False
    return render(
        request,
        template_name,
        {"error_message_name": error_msg},
    )


def __gos_handle_login(request, student):
    msg, good_result = student.handle_signin_attempt()
    request.session["result_msg"] = msg
    request.session["good_result"] = good_result
    return HttpResponseRedirect(reverse("gos_signin"))


class ActiveManifest(generic.TemplateView):
    template_name = "attendance/signed_in_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["gos_students"] = [
            student for student in GosStudent.objects.all() if student.is_logged_in()
        ]
        return context


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

    def __repr__(self):
        return f"CalendarEvent - {type(self.time_in)}"


def create_calendar_events_from_attendance(attendance_model, title, color):
    visits = attendance_model.objects.values("time_in__date").annotate(
        xyz=Count("time_in__date")
    )

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
