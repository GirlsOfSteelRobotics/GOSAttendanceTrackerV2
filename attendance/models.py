import abc
import datetime
from typing import Optional, Tuple

from django.db import models
from django.utils import timezone


class InOutTimeMixin:
    def is_logged_in(self):
        active_time = self.time_since_last_login()
        print(active_time)
        if active_time is None:
            return False

        if active_time > timezone.timedelta(hours=18):
            return False

        last_login = self.get_last_login()
        return last_login.time_out is None

    def time_since_last_login(self) -> Optional[datetime.timedelta]:
        last_login = self.get_last_login()
        if last_login is None:
            return None

        now = timezone.now()
        delta = now - last_login.time_in
        return delta

    def get_last_login(self):
        logins = self._attendance_model().order_by("-time_in")
        if logins.count() > 0:
            return logins[0]
        return None

    def handle_signin_attempt(self) -> Tuple[Optional[str], bool]:
        DEBOUNCE_TIME_MINUTES = 1

        msg = None
        good_result = False

        username = self._full_name()

        if self.is_logged_in():
            time_from_login = self.time_since_last_login()
            time_from_login_sec = int(time_from_login.total_seconds())
            if time_from_login < datetime.timedelta(minutes=DEBOUNCE_TIME_MINUTES):
                msg = f"{username} tapped twice in {time_from_login_sec} seconds, ignoring input. Please try again after {DEBOUNCE_TIME_MINUTES} minutes"
            else:
                hours = time_from_login_sec // 3600
                minutes = (time_from_login_sec % 3600) // 60
                msg = f"{username} Logged out after {hours:02}:{minutes:02}."
                self._log_out()
                good_result = True
        else:
            self._log_in()
            msg = f"{username} Logged in"
            good_result = True

        return msg, good_result

    @abc.abstractmethod
    def _attendance_model(self):
        raise NotImplementedError()

    @abc.abstractmethod
    def _log_in(self):
        raise NotImplementedError()

    @abc.abstractmethod
    def _log_out(self):
        raise NotImplementedError()

    @abc.abstractmethod
    def _full_name(self):
        raise NotImplementedError()


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


class FieldBuilder(models.Model):
    full_name = models.CharField(max_length=100)
    forms_completed = models.BooleanField(default=False)

    def __str__(self):
        return self.full_name


class ScraVisitor(models.Model):
    full_name = models.CharField(max_length=100)
    team_number = models.IntegerField()

    def __str__(self):
        return self.full_name


class AttendanceMixin(models.Model):
    time_in = models.DateTimeField("Time In")
    time_out = models.DateTimeField("Time Out", null=True)

    def get_duration(self):
        out = self.time_out or self.time_in + datetime.timedelta(hours=2)
        return out - self.time_in

    class Meta:
        abstract = True


class GosAttendance(AttendanceMixin):
    student = models.ForeignKey(GosStudent, on_delete=models.CASCADE)
    purpose = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.student} {self.time_in}-{self.time_out}"


class FieldBuilderAttendance(AttendanceMixin):
    field_builder = models.ForeignKey(FieldBuilder, on_delete=models.CASCADE)


class ScraVisitorAttendance(AttendanceMixin):
    scra_visitor = models.ForeignKey(ScraVisitor, on_delete=models.CASCADE)
    purpose = models.CharField(max_length=100)
