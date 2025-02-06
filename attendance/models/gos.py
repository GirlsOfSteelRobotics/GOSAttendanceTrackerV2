from django.db import models
from django.utils import timezone

from attendance.models.mixins import InOutTimeMixin, AttendanceMixin


class GosStudent(models.Model, InOutTimeMixin):
    rfid = models.IntegerField()
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)

    def __str__(self):  # pragma: no cover
        return self.full_name()

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
