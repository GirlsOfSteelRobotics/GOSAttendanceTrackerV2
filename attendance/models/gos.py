from django.db import models
from django.utils import timezone

from attendance.models.mixins import InOutTimeMixin, AttendanceMixin


class GosSubteam(models.TextChoices):
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


class GosProgram(models.TextChoices):
    UNASSIGNED = "UNASSIGNED"
    FRC = "FRC"
    FTC = "FTC"


class GosPreseasonCrew(models.TextChoices):
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


class GosGradeLevel(models.IntegerChoices):
    UNASSIGNED = 0
    MENTOR = 13
    SENIOR = 12
    JUNIOR = 11
    SOPHOMORE = 10
    FRESHMAN = 9
    EIGHTH = 8
    SEVENTH = 7


class GosStudent(models.Model, InOutTimeMixin):
    rfid = models.IntegerField()
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    gos_program = models.CharField(
        choices=GosProgram.choices, default=GosProgram.UNASSIGNED, max_length=20
    )
    preseason_crew = models.CharField(
        choices=GosPreseasonCrew.choices,
        default=GosPreseasonCrew.UNASSIGNED,
        max_length=20,
    )
    subteam = models.CharField(
        choices=GosSubteam.choices, default=GosSubteam.UNASSIGNED, max_length=20
    )
    grade = models.IntegerField(choices=GosGradeLevel, default=GosGradeLevel.UNASSIGNED)

    def __str__(self):  # pragma: no cover
        return self.full_name() + f" ({self.gos_program} {self.subteam} - {self.grade})"

    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def _get_attendance_set(self):
        return self.gosattendance_set

    def _log_in(self):
        return GosAttendance.objects.create(student=self, time_in=timezone.now())

    def _full_name(self):
        return self.full_name()


class GosAttendance(AttendanceMixin):
    student = models.ForeignKey(GosStudent, on_delete=models.CASCADE)
    purpose = models.CharField(max_length=100)

    def __str__(self):  # pragma: no cover
        return f"{self.student} {self.time_in}-{self.time_out}"
