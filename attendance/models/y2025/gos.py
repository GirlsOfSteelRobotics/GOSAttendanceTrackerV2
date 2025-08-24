from django.db import models
from django.utils import timezone

from attendance.models.mixins import InOutTimeMixin, AttendanceMixin


class GosSubteam2025(models.TextChoices):
    UNASSIGNED = "UNASSIGNED"

    Design = "Design"
    Mechanical = "Mechanical"
    Electrical = "Electrical"
    Software = "Software"
    DataScience = "Data Science"

    FtcHypatia = "FTC Hypatia"
    FtcHopper = "FTC Hopper"
    FtcLovelace = "FTC Lovelace"
    FtcJuniors = "FTC Juniors"


class GosProgram2025(models.TextChoices):
    UNASSIGNED = "UNASSIGNED"
    FRC = "FRC"
    FTC = "FTC"


class GosPreseasonCrew2025(models.TextChoices):
    UNASSIGNED = "UNASSIGNED"

    Crew1 = "Crew 1"
    Crew2 = "Crew 2"
    Crew3 = "Crew 3"
    Crew4 = "Crew 4"
    Crew5 = "Crew 5"
    Crew6 = "Crew 6"
    Crew7 = "Crew 7"
    Crew8 = "Crew 8"

    IndependentProjectDataScience = "IP Data Science"
    IndependentProjectMeepMeep = "IP Meep Meep"
    IndependentCurriculum = "IP Curriculum"

    FloatingMentor = "Floating Mentor"


class GosGradeLevel2025(models.IntegerChoices):
    UNASSIGNED = 0
    MENTOR = 13
    SENIOR = 12
    JUNIOR = 11
    SOPHOMORE = 10
    FRESHMAN = 9
    EIGHTH = 8
    SEVENTH = 7


class GosStudent2025(models.Model, InOutTimeMixin):
    rfid = models.IntegerField()
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    gos_program = models.CharField(
        choices=GosProgram2025.choices, default=GosProgram2025.UNASSIGNED, max_length=20
    )
    preseason_crew = models.CharField(
        choices=GosPreseasonCrew2025.choices,
        default=GosPreseasonCrew2025.UNASSIGNED,
        max_length=20,
    )
    subteam = models.CharField(
        choices=GosSubteam2025.choices, default=GosSubteam2025.UNASSIGNED, max_length=20
    )
    grade = models.IntegerField(
        choices=GosGradeLevel2025, default=GosGradeLevel2025.UNASSIGNED
    )

    def __init__(self, *kargs, **kwargs):
        models.Model.__init__(self, *kargs, **kwargs)
        self.gosattendance_set = self.gosattendance2025_set

    def __str__(self):  # pragma: no cover
        return self.full_name() + f" ({self.gos_program} {self.subteam} - {self.grade})"

    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def _get_attendance_set(self):
        return self.gosattendance2025_set

    def _log_in(self):
        return GosAttendance2025.objects.create(student=self, time_in=timezone.now())

    def _full_name(self):
        return self.full_name()


class GosAttendance2025(AttendanceMixin):
    student = models.ForeignKey(GosStudent2025, on_delete=models.CASCADE)
    purpose = models.CharField(max_length=100)

    def __str__(self):  # pragma: no cover
        return f"{self.student} {self.time_in}-{self.time_out}"
