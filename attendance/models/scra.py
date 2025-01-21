from django.db import models

from attendance.models.mixins import InOutTimeMixin, AttendanceMixin


class ScraVisitor(models.Model, InOutTimeMixin):
    full_name = models.CharField(max_length=100)
    team_number = models.IntegerField()

    def __str__(self):
        return self.full_name


class ScraVisitorAttendance(AttendanceMixin):
    scra_visitor = models.ForeignKey(ScraVisitor, on_delete=models.CASCADE)
    purpose = models.CharField(max_length=100)
