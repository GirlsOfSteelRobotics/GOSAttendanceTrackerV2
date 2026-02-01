from django.views import generic

from attendance.models import (
    FieldBuilder,
    FieldBuilderAttendance,
    GosAttendance,
    GosStudent,
    ScraVisitor,
    ScraVisitorAttendance,
    GosGradeLevel,
)
from attendance.views.utils import (
    create_calendar_events_from_attendance,
    get_navbar_context,
)


class IndexView(generic.TemplateView):
    template_name = "attendance/index.html"

    def get_context_data(self, **kwargs):
        calendar_events = []

        GOS_PROGRAMS_DEFINED = True

        if GOS_PROGRAMS_DEFINED:
            calendar_events.extend(
                create_calendar_events_from_attendance(
                    GosAttendance.objects.filter(student__gos_program="FRC"),
                    "GOS FRC",
                    "blue",
                )
            )
            calendar_events.extend(
                create_calendar_events_from_attendance(
                    GosAttendance.objects.filter(student__gos_program="FTC"),
                    "GOS FTC",
                    "orange",
                )
            )
            calendar_events.extend(
                create_calendar_events_from_attendance(
                    GosAttendance.objects.filter(
                        student__gos_program="UNASSIGNED"
                    ).exclude(student__grade=GosGradeLevel.MENTOR),
                    "GOS Unassigned",
                    "gray",
                )
            )
            calendar_events.extend(
                create_calendar_events_from_attendance(
                    GosAttendance.objects.filter(student__grade=GosGradeLevel.MENTOR),
                    "GOS Mentors",
                    "green",
                )
            )
        else:
            calendar_events.extend(
                create_calendar_events_from_attendance(
                    GosAttendance.objects.exclude(student__grade=GosGradeLevel.MENTOR),
                    "GOS Students",
                    "blue",
                )
            )
            calendar_events.extend(
                create_calendar_events_from_attendance(
                    GosAttendance.objects.filter(student__grade=GosGradeLevel.MENTOR),
                    "GOS Mentors",
                    "green",
                )
            )

        calendar_events.extend(
            create_calendar_events_from_attendance(
                ScraVisitorAttendance.objects.all(), "SCRA", "black"
            )
        )

        calendar_events.extend(
            create_calendar_events_from_attendance(
                FieldBuilderAttendance.objects.all(), "Field Builders", "purple"
            )
        )

        context = super().get_context_data(**kwargs)
        context.update(get_navbar_context())
        context["calendar_events"] = calendar_events
        return context


class ActiveManifest(generic.TemplateView):
    template_name = "attendance/signed_in_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(get_navbar_context())
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
