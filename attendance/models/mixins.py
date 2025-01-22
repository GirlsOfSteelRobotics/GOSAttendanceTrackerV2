import abc
import datetime
from typing import Optional, Tuple

from django.db import models
from django.utils import timezone


class InOutTimeMixin:
    def is_logged_in(self) -> bool:
        active_time = self.time_since_last_login()
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
        logins = self._get_attendance_set().order_by("-time_in")
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

    def num_meetings(self):
        return len(self._get_attendance_set().all())

    def num_hours(self):
        total_time = sum(
            [x.get_duration() for x in self._get_attendance_set().all()],
            datetime.timedelta(),
        )
        return total_time.total_seconds() / 3600

    def _log_out(self):
        last_login = self.get_last_login()
        last_login.time_out = timezone.now()
        last_login.save()

    @abc.abstractmethod
    def _get_attendance_set(self):
        raise NotImplementedError()

    @abc.abstractmethod
    def _log_in(self):
        raise NotImplementedError()

    @abc.abstractmethod
    def _full_name(self) -> str:
        raise NotImplementedError()


class AttendanceMixin(models.Model):
    time_in = models.DateTimeField("Time In")
    time_out = models.DateTimeField("Time Out", null=True)

    def get_duration(self):
        out = self.time_out or self.time_in + datetime.timedelta(hours=2)
        return out - self.time_in

    class Meta:
        abstract = True
