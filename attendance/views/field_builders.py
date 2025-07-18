import datetime

from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views import generic

from attendance.models import FieldBuilder, FieldBuilderAttendance
from attendance.views.utils import get_navbar_context, CalendarEvent


class FieldBuilderList(generic.TemplateView):
    template_name = "attendance/field_builders/fieldbuilder_list.html"

    def get_context_data(self):

        calendar_events = []

        for fb_att in FieldBuilderAttendance.objects.all():
            calendar_events.append(
                CalendarEvent(
                    time_in=datetime.datetime.fromisoformat(fb_att.time_in.isoformat()),
                    time_out=None,
                    title=f"{fb_att.field_builder.full_name}",
                    show_as_all_day=False,
                )
            )

        context = get_navbar_context()
        context["calendar_events"] = calendar_events
        context["field_builders"] = FieldBuilder.objects.all()
        return context


class FieldBuildersSignin(generic.TemplateView):
    template_name = "attendance/field_builders/signin.html"

    def get_context_data(self):
        context = {}
        context["field_builders"] = FieldBuilder.objects.all()
        return context


def field_builders_log_attendance(request):
    full_name = request.POST["full_name"].strip()
    if len(full_name) == 0:
        request.session["result_msg"] = "You must enter a full name."
        request.session["good_result"] = False
        return HttpResponseRedirect(reverse("field_builders_signin"))

    fb, is_new = FieldBuilder.objects.get_or_create(full_name=full_name)

    msg, good_result = fb.handle_signin_attempt()
    if is_new:
        msg += ". As a new visitor, please make sure you have filled out the CMU forms"

    request.session["result_msg"] = msg
    request.session["good_result"] = good_result
    return HttpResponseRedirect(reverse("field_builders_signin"))
