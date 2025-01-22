import datetime

from django.db import models
from django.utils import timezone

from attendance.models.mixins import InOutTimeMixin, AttendanceMixin
from attendance.models.sheets_backend import GoogleSheetsBackend


class GosStudent(models.Model, InOutTimeMixin):
    rfid = models.IntegerField()
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)

    def __str__(self):
        return self.full_name()

    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def _get_attendance_set(self):
        return self.gosattendance_set

    def _log_in(self):
        attendance = GosAttendance.objects.create(student=self, time_in=timezone.now())
        sheets_backend = GoogleSheetsBackend()
        sheets_backend.gos_signin(
            attendance.time_in, attendance.student.rfid, attendance.student.full_name()
        )

    def _full_name(self):
        return self.full_name()


class GosAttendance(AttendanceMixin):
    student = models.ForeignKey(GosStudent, on_delete=models.CASCADE)
    purpose = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.student} {self.time_in}-{self.time_out}"
