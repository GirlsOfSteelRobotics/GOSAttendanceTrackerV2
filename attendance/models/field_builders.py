from django.db import models

from attendance.models.mixins import AttendanceMixin


class FieldBuilder(models.Model):
    full_name = models.CharField(max_length=100)
    forms_completed = models.BooleanField(default=False)

    def __str__(self):
        return self.full_name


class FieldBuilderAttendance(AttendanceMixin):
    field_builder = models.ForeignKey(FieldBuilder, on_delete=models.CASCADE)
