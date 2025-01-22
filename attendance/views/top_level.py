from django.views import generic

from attendance.models import ScraVisitorAttendance, FieldBuilderAttendance, ScraVisitor, FieldBuilder
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

        calendar_events.extend(
            create_calendar_events_from_attendance(
                ScraVisitorAttendance.objects.all(), "SCRA", "black"
            )
        )

        calendar_events.extend(
            create_calendar_events_from_attendance(
                FieldBuilderAttendance.objects.all(), "Field Builders", "green"
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
        context["scra_visitors"] = [
            visitor for visitor in ScraVisitor.objects.all() if visitor.is_logged_in()
        ]
        context["field_builders"] = [
            visitor for visitor in FieldBuilder.objects.all() if visitor.is_logged_in()
        ]
        return context
