from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import generic
from django import forms

from attendance.models import (
    GosProgram,
    GosSubteam,
    GosGradeLevel,
    GosStudent,
    GosPreseasonCrew,
    GosBusinessSubteams,
)
from attendance.models.y2025.gos import GosStudent2025
from attendance.views.plotting_utils import (
    render_count_pie_chart,
    render_box_and_whisker_plot,
    render_cumulative_hours_plot,
    render_hours_scatter,
)
from attendance.views.utils import get_navbar_context, get_recommended_hour_lines
import pandas as pd


class GosStudentSummaryView(generic.ListView):
    model = GosStudent
    template_name = "attendance/gos/gosstudent_list.html"

    ordering = ["first_name"]

    def get_queryset(self):
        return GosStudent.objects.exclude(grade=GosGradeLevel.MENTOR).order_by("first_name")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(get_navbar_context())

        plots = []
        plots.append(
            render_cumulative_hours_plot(
                GosStudent.objects.exclude(grade=GosGradeLevel.MENTOR), get_recommended_hour_lines()
            )
        )

        context["plots"] = plots

        return context


class GosPresasonCrewDetail(generic.TemplateView):
    template_name = "attendance/gos/ftc_crew_detail.html"

    def get_context_data(self, crew):
        students = GosStudent.objects.filter(preseason_crew=crew).order_by("first_name")
        context = get_navbar_context()
        context["crew_name"] = crew
        context["students"] = students
        context["plots"] = [
            render_cumulative_hours_plot(students, get_recommended_hour_lines())
        ]
        return context


class GosPresasonCrewList(generic.TemplateView):
    template_name = "attendance/gos/ftc_crew_list.html"

    def get_context_data(self):
        crews = {}
        for crew_name, _ in GosPreseasonCrew.choices:
            students = GosStudent.objects.filter(preseason_crew=crew_name).order_by(
                "first_name"
            )
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


class GosBusinessSubteamDetail(generic.TemplateView):
    template_name = "attendance/gos/business_subteam_detail.html"

    def get_context_data(self, business_subteam):
        students = GosStudent.objects.filter(
            business_subteam=business_subteam
        ).order_by("first_name")
        context = get_navbar_context()
        context["business_subteam"] = business_subteam
        context["students"] = students
        context["plots"] = [
            render_cumulative_hours_plot(students, get_recommended_hour_lines())
        ]
        return context


class GosBusinessSubteamList(generic.TemplateView):
    template_name = "attendance/gos/business_subteam_list.html"

    def get_context_data(self):
        subteams = {}
        for subteam_name, _ in GosBusinessSubteams.choices:
            print(subteam_name)
            students = GosStudent.objects.filter(
                business_subteam=subteam_name
            ).order_by("first_name")
            print(students)
            subteams[subteam_name] = students

        df = pd.DataFrame(list(GosStudent.objects.all().values()))

        plots = []
        plots.append(
            render_count_pie_chart(df, "business_subteam", "id", title="Subteam Sizes")
        )
        plots.append(
            render_box_and_whisker_plot(
                df,
                "business_subteam",
                [student.num_hours() for student in GosStudent.objects.all()],
                title="Subteam Hours",
            )
        )

        context = get_navbar_context()
        context["business_subteams"] = subteams
        context["plots"] = plots
        return context


class GosProgramDetail(generic.TemplateView):
    template_name = "attendance/gos/gos_program_detail.html"

    def get_context_data(self, program):
        students = GosStudent.objects.filter(gos_program=program).order_by("first_name")
        context = get_navbar_context()
        context["program_name"] = program
        context["students"] = students

        context["plots"] = [
            render_cumulative_hours_plot(students, get_recommended_hour_lines())
        ]
        return context


class GosProgramList(generic.TemplateView):
    template_name = "attendance/gos/gos_program_list.html"

    def get_context_data(self):
        programs = {}
        for program_name, _ in GosProgram.choices:
            students = GosStudent.objects.filter(gos_program=program_name).order_by(
                "first_name"
            )
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
        context["plots"] = [render_hours_scatter(kwargs["object"])]
        return context


class GosGradeYearList(generic.TemplateView):
    template_name = "attendance/gos/grade_year_list.html"

    def get_context_data(self):
        grades = {}
        for grade, _ in GosGradeLevel.choices:
            students = GosStudent.objects.filter(grade=grade).order_by("first_name")
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
        students = GosStudent.objects.filter(grade=grade_year).order_by("first_name")

        context = get_navbar_context()
        context["grade"] = grade_year
        context["students"] = students
        context["plots"] = [
            render_cumulative_hours_plot(students, get_recommended_hour_lines())
        ]
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

        frc_students = GosStudent.objects.filter(gos_program="FRC").order_by(
            "first_name"
        )
        ftc_students = GosStudent.objects.filter(gos_program="FTC").order_by(
            "first_name"
        )

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
        students = GosStudent.objects.filter(subteam=subteam).order_by("first_name")
        context = get_navbar_context()
        context["subteam"] = subteam
        context["students"] = students
        context["plots"] = [
            render_cumulative_hours_plot(students, get_recommended_hour_lines())
        ]
        return context


class GosNewStudentForm(forms.ModelForm):
    class Meta:
        model = GosStudent
        fields = ["first_name", "last_name", "grade", "rfid"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name in self.fields:
            self.fields[field_name].widget.attrs.update({"class": "form-control"})

    def clean(self):
        super(GosNewStudentForm, self).clean()

        students = GosStudent.objects.filter(
            first_name=self.cleaned_data["first_name"],
            last_name=self.cleaned_data["last_name"],
        )
        if students:
            self._errors["first_name"] = self.error_class(
                ["Duplicate Name Encountered"]
            )

        if self.cleaned_data["rfid"] is None:
            last_year_student = GosStudent2025.objects.filter(
                first_name=self.cleaned_data["first_name"],
                last_name=self.cleaned_data["last_name"],
            )
            if len(last_year_student) == 1:
                self.cleaned_data["rfid"] = last_year_student[0].rfid
            else:
                self._errors["rfid"] = self.error_class(
                    ["Name not found in 2025 database, you must specify an RFID"]
                )

        return self.cleaned_data

    def save(self, commit=True):
        student = forms.ModelForm.save(self, commit=True)
        student.handle_signin_attempt()


def new_student(request):
    if request.method == "POST":
        form = GosNewStudentForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("new_student")
    else:
        form = GosNewStudentForm()

    context = get_navbar_context()
    context["form"] = form
    return render(request, "attendance/gos/new_student_form.html", context)
