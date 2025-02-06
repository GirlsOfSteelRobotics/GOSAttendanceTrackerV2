from django.db import models
from django.utils import timezone

from attendance.models.mixins import InOutTimeMixin, AttendanceMixin


class FieldBuilder(models.Model, InOutTimeMixin):
    full_name = models.CharField(max_length=100)
    forms_completed = models.BooleanField(default=False)

    def __str__(self):  # pragma: no cover
        return self.full_name

    def _get_attendance_set(self):
        return self.fieldbuilderattendance_set

    def _log_in(self):
        return FieldBuilderAttendance.objects.create(
            field_builder=self, time_in=timezone.now()
        )

    def _full_name(self):
        return self.full_name


class FieldBuilderAttendance(AttendanceMixin):
    field_builder = models.ForeignKey(FieldBuilder, on_delete=models.CASCADE)

    def __str__(self):  # pragma: no cover
        return f"{self.field_builder.full_name}: {self.time_in} - {self.time_out}"
