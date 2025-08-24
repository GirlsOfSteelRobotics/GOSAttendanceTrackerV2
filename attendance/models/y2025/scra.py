from django.db import models
from django.utils import timezone

from attendance.models.mixins import InOutTimeMixin, AttendanceMixin


class ScraVisitor2025(models.Model, InOutTimeMixin):
    full_name = models.CharField(max_length=100)
    team_number = models.IntegerField()

    def __init__(self, *kargs, **kwargs):
        models.Model.__init__(self, *kargs, **kwargs)
        self.scravisitorattendance_set = self.scravisitorattendance2025_set

    def __str__(self):  # pragma: no cover
        return f"{self.full_name} - {self.team_number}"

    def _get_attendance_set(self):
        return self.scravisitorattendance2025_set

    def _log_in(self):
        return ScraVisitorAttendance2025.objects.create(
            scra_visitor=self, time_in=timezone.now()
        )

    def _full_name(self):
        return self.full_name


class ScraVisitorAttendance2025(AttendanceMixin):
    scra_visitor = models.ForeignKey(ScraVisitor2025, on_delete=models.CASCADE)
    purpose = models.CharField(max_length=100)

    def __str__(self):  # pragma: no cover
        return f"{self.scra_visitor.full_name}: {self.time_in} - {self.time_out}"
