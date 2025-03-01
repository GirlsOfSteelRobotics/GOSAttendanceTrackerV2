from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views import generic

from attendance.models import ScraVisitor, ScraVisitorAttendance
from attendance.views.utils import (
    create_calendar_events_from_attendance,
)


class ScraSignin(generic.TemplateView):
    template_name = "attendance/scra/signin.html"

    def get_context_data(self):
        team_numbers = (
            ScraVisitor.objects.all()
            .values("team_number")
            .distinct()
            .order_by("team_number")
        )

        teams_data = {}
        for fields in team_numbers:
            team_number = fields["team_number"]
            teams_data[team_number] = list(ScraVisitor.objects.filter(
                team_number=team_number
            ))
            # TODO filter bad names on creation, not here
            bad_names = []
            for visitor in teams_data[team_number]:
                if "\\" in visitor.full_name or "\"" in visitor.full_name:
                    bad_names.append(visitor)

            for bad_name in bad_names:
                teams_data[team_number].remove(bad_name)

        context = {}
        context["teams"] = teams_data
        return context


class ScraVisitorList(generic.TemplateView):
    template_name = "attendance/scra/scravisitor_list.html"

    def get_context_data(self):
        team_numbers = (
            ScraVisitor.objects.all()
            .values("team_number")
            .distinct()
            .order_by("team_number")
        )

        calendar_events = []

        teams_data = {}
        for fields in team_numbers:
            team_number = fields["team_number"]
            teams_data[team_number] = ScraVisitor.objects.filter(
                team_number=team_number
            )

            calendar_events.extend(
                create_calendar_events_from_attendance(
                    ScraVisitorAttendance.objects.filter(
                        scra_visitor__team_number=team_number
                    ),
                    f"Team {team_number}",
                )
            )

        context = {}
        context["teams"] = teams_data
        context["calendar_events"] = calendar_events
        return context


def scra_log_attendance(request):
    team_number = int(request.POST["team_number"])
    full_name = request.POST["full_name"].strip()
    if len(full_name) == 0:
        request.session["result_msg"] = "You must enter a full name."
        request.session["good_result"] = False
        return HttpResponseRedirect(reverse("scra_signin"))

    scra_user, is_new = ScraVisitor.objects.get_or_create(
        team_number=team_number, full_name=full_name
    )

    msg, good_result = scra_user.handle_signin_attempt()
    if is_new:
        msg += ". As a new visitor, please make sure you have filled out the CMU forms"

    request.session["result_msg"] = msg
    request.session["good_result"] = good_result
    return HttpResponseRedirect(reverse("scra_signin"))
