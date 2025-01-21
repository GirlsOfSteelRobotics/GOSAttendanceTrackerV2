from django.views import generic

from attendance.models.gos import GosStudent, GosAttendance
from attendance.views.utils import create_calendar_events_from_attendance


class IndexView(generic.TemplateView):
    template_name = "attendance/index.html"

    def get_context_data(self, **kwargs):
        calendar_events = []

        calendar_events.extend(
            create_calendar_events_from_attendance(
                GosAttendance.objects.all(), "GOS", "blue"
            )
        )

        context = super().get_context_data(**kwargs)
        context["calendar_events"] = calendar_events
        return context


class ActiveManifest(generic.TemplateView):
    template_name = "attendance/signed_in_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["gos_students"] = [
            student for student in GosStudent.objects.all() if student.is_logged_in()
        ]
        return context
