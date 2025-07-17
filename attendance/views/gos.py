from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.views import generic

from attendance.models import GosProgram, GosSubteam, GosGradeLevel
from attendance.models.gos import GosStudent, GosPreseasonCrew
from attendance.views.plotting_utils import (
    render_count_pie_chart,
    render_box_and_whisker_plot,
    render_cumulative_hours_plot,
)
from attendance.views.utils import get_navbar_context
import pandas as pd


class GosStudentSummaryView(generic.ListView):
    model = GosStudent
    template_name = "attendance/gos/gosstudent_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(get_navbar_context())

        plots = []
        plots.append(render_cumulative_hours_plot(GosStudent.objects.all()))

        context["plots"] = plots

        return context


class GosPresasonCrewDetail(generic.TemplateView):
    template_name = "attendance/gos/ftc_crew_detail.html"

    def get_context_data(self, crew):
        students = GosStudent.objects.filter(preseason_crew=crew)
        context = get_navbar_context()
        context["crew_name"] = crew
        context["students"] = students
        context["plots"] = [render_cumulative_hours_plot(students)]
        return context


class GosPresasonCrewList(generic.TemplateView):
    template_name = "attendance/gos/ftc_crew_list.html"

    def get_context_data(self):
        crews = {}
        for crew_name, _ in GosPreseasonCrew.choices:
            students = GosStudent.objects.filter(preseason_crew=crew_name)
            crews[crew_name] = students

        df = pd.DataFrame(list(GosStudent.objects.all().values()))

        plots = []
        plots.append(
            render_count_pie_chart(df, "preseason_crew", "id", title="Crew Sizes")
        )
        plots.append(
            render_box_and_whisker_plot(
                df,
                "preseason_crew",
                [student.num_hours() for student in GosStudent.objects.all()],
                title="Crew Hours",
            )
        )

        context = get_navbar_context()
        context["crews"] = crews
        context["plots"] = plots
        return context


class GosProgramDetail(generic.TemplateView):
    template_name = "attendance/gos/gos_program_detail.html"

    def get_context_data(self, program):
        students = GosStudent.objects.filter(gos_program=program)
        context = get_navbar_context()
        context["program_name"] = program
        context["students"] = students

        context["plots"] = [render_cumulative_hours_plot(students)]
        return context


class GosProgramList(generic.TemplateView):
    template_name = "attendance/gos/gos_program_list.html"

    def get_context_data(self):
        programs = {}
        for program_name, _ in GosProgram.choices:
            students = GosStudent.objects.filter(gos_program=program_name)
            programs[program_name] = students

        df = pd.DataFrame(list(GosStudent.objects.all().values()))
        plots = []
        plots.append(
            render_count_pie_chart(df, "gos_program", "id", title="Program Sizes")
        )
        plots.append(
            render_box_and_whisker_plot(
                df,
                "gos_program",
                [student.num_hours() for student in GosStudent.objects.all()],
                title="Program Hours",
            )
        )

        context = get_navbar_context()
        context["programs"] = programs
        context["plots"] = plots
        return context


class GosStudentDetailView(generic.DetailView):
    model = GosStudent
    template_name = "attendance/gos/gosstudent_detail.html"
    slug_url_kwarg = "rfid"
    slug_field = "rfid"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(get_navbar_context())
        context["attendance"] = []
        return context


class GosGradeYearList(generic.TemplateView):
    template_name = "attendance/gos/grade_year_list.html"

    def get_context_data(self):
        grades = {}
        for grade, _ in GosGradeLevel.choices:
            students = GosStudent.objects.filter(grade=grade)
            grades[grade] = students

        df = pd.DataFrame(list(GosStudent.objects.all().values()))
        plots = []
        plots.append(render_count_pie_chart(df, "grade", "id", title="Grade Sizes"))
        plots.append(
            render_box_and_whisker_plot(
                df,
                "grade",
                [student.num_hours() for student in GosStudent.objects.all()],
                title="Grade Hours",
            )
        )
        context = get_navbar_context()
        context["grades"] = grades
        context["plots"] = plots
        return context


class GosGradeYearDetail(generic.TemplateView):
    template_name = "attendance/gos/grade_year_detail.html"

    def get_context_data(self, grade_year):
        students = GosStudent.objects.filter(grade=grade_year)

        context = get_navbar_context()
        context["grade"] = grade_year
        context["students"] = students
        context["plots"] = [render_cumulative_hours_plot(students)]
        return context


def gos_signin(request):
    return render(request, "attendance/gos/signin.html")


def gos_log_attendance_rfid(request):
    rfid = request.POST["rfid"]
    try:
        rfid = int(rfid)
    except ValueError:
        return __login_failure_redirect(
            request, f"Invalid rfid '{rfid}'", "attendance/gos/signin.html"
        )

    students = GosStudent.objects.filter(rfid=rfid)
    if not students:
        return __login_failure_redirect(
            request, f"No student found with RFID {rfid}", "attendance/gos/signin.html"
        )

    return __gos_handle_login(request, students[0])


def gos_log_attendance_name(request):
    full_name = request.POST["full_name"].strip()
    name_parts = full_name.split(" ")
    if len(name_parts) != 2:
        return __login_failure_redirect(
            request,
            f"Invalid student name {full_name}, could not split the name into two parts",
            "attendance/gos/signin.html",
        )

    first_name, last_name = name_parts
    students = GosStudent.objects.filter(first_name=first_name, last_name=last_name)
    if not students:
        return __login_failure_redirect(
            request,
            f"Invalid student name {full_name}",
            "attendance/gos/signin.html",
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


class GosSubteamList(generic.TemplateView):
    template_name = "attendance/gos/subteam_list.html"

    def get_context_data(self):
        subteams = {}
        for subteam_name, _ in GosSubteam.choices:
            students = GosStudent.objects.filter(subteam=subteam_name)
            subteams[subteam_name] = students

        frc_students = GosStudent.objects.filter(gos_program="FRC")
        ftc_students = GosStudent.objects.filter(gos_program="FTC")

        frc_df = pd.DataFrame(list(frc_students.values()))
        ftc_df = pd.DataFrame(list(ftc_students.values()))
        plots = []
        plots.append(
            render_count_pie_chart(frc_df, "subteam", "id", title="FRC Subteam Sizes")
        )
        plots.append(
            render_box_and_whisker_plot(
                frc_df,
                "subteam",
                [student.num_hours() for student in frc_students],
                title="FRC Program Hours",
            )
        )

        plots.append(
            render_count_pie_chart(ftc_df, "subteam", "id", title="FTC Subteam Sizes")
        )
        plots.append(
            render_box_and_whisker_plot(
                ftc_df,
                "subteam",
                [student.num_hours() for student in ftc_students],
                title="FTC Program Hours",
            )
        )

        context = get_navbar_context()
        context["subteams"] = subteams
        context["plots"] = plots
        return context


class GosSubteamDetail(generic.TemplateView):
    template_name = "attendance/gos/subteam_detail.html"

    def get_context_data(self, subteam):
        students = GosStudent.objects.filter(subteam=subteam)
        context = get_navbar_context()
        context["students"] = students
        context["plots"] = [render_cumulative_hours_plot(students)]
        return context
