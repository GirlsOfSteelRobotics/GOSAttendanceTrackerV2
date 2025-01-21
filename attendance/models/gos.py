import datetime

from django.db import models
from django.utils import timezone

from attendance.models.mixins import InOutTimeMixin, AttendanceMixin


class GosStudent(models.Model, InOutTimeMixin):
    rfid = models.IntegerField()
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)

    def __str__(self):
        return self.full_name()

    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def num_meetings(self):
        return len(self.gosattendance_set.all())

    def num_hours(self):
        total_time = sum(
            [x.get_duration() for x in self.gosattendance_set.all()],
            datetime.timedelta(),
        )
        return total_time.total_seconds() / 3600

    def _attendance_model(self):
        return self.gosattendance_set

    def _log_in(self):
        GosAttendance.objects.create(student=self, time_in=timezone.now())

    def _log_out(self):
        last_login = self.get_last_login()
        last_login.time_out = timezone.now()
        last_login.save()

    def _full_name(self):
        return self.full_name()


class GosAttendance(AttendanceMixin):
    student = models.ForeignKey(GosStudent, on_delete=models.CASCADE)
    purpose = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.student} {self.time_in}-{self.time_out}"
