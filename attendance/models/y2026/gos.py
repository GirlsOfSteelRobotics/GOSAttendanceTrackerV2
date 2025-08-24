from django.db import models
from django.utils import timezone

from attendance.models.mixins import InOutTimeMixin, AttendanceMixin


class GosSubteam2026(models.TextChoices):
    UNASSIGNED = "UNASSIGNED"


class GosProgram2026(models.TextChoices):
    UNASSIGNED = "UNASSIGNED"


class GosPreseasonCrew2026(models.TextChoices):
    UNASSIGNED = "UNASSIGNED"


class GosGradeLevel2026(models.IntegerChoices):
    SENIOR = 12
    JUNIOR = 11
    SOPHOMORE = 10
    FRESHMAN = 9
    EIGHTH = 8
    SEVENTH = 7


class GosStudent2026(models.Model, InOutTimeMixin):
    rfid = models.IntegerField(unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    gos_program = models.CharField(
        choices=GosProgram2026.choices, default=GosProgram2026.UNASSIGNED, max_length=20
    )
    preseason_crew = models.CharField(
        choices=GosPreseasonCrew2026.choices,
        default=GosPreseasonCrew2026.UNASSIGNED,
        max_length=20,
    )
    subteam = models.CharField(
        choices=GosSubteam2026.choices, default=GosSubteam2026.UNASSIGNED, max_length=20
    )
    grade = models.IntegerField(choices=GosGradeLevel2026)

    def __str__(self):  # pragma: no cover
        return self.full_name() + f" ({self.gos_program} {self.subteam} - {self.grade})"

    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def _get_attendance_set(self):
        return self.gosattendance2026_set

    def _log_in(self):
        return GosAttendance2026.objects.create(student=self, time_in=timezone.now())

    def _full_name(self):
        return self.full_name()


class GosAttendance2026(AttendanceMixin):
    student = models.ForeignKey(GosStudent2026, on_delete=models.CASCADE)
    purpose = models.CharField(max_length=100)

    def __str__(self):  # pragma: no cover
        return f"{self.student} {self.time_in}-{self.time_out}"
