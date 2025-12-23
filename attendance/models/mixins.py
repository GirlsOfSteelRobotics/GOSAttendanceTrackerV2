import abc
import datetime
from typing import Optional, Tuple

from django.db import models
from django.utils import timezone

from attendance.models.date_ranges import (
    get_filter_attendance_by_date_range_query,
)

CROSS_POST_LOGINS = True


def set_cross_post_login(new_val):
    global CROSS_POST_LOGINS
    CROSS_POST_LOGINS = new_val


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
        now = timezone.now()
        now_str = now.strftime("%I:%M %p")

        if self.is_logged_in():
            time_from_login = self.time_since_last_login()
            time_from_login_sec = int(time_from_login.total_seconds())
            if time_from_login < datetime.timedelta(minutes=DEBOUNCE_TIME_MINUTES):
                msg = f"{username} tapped twice in {time_from_login_sec} seconds, ignoring input. Please try again after {DEBOUNCE_TIME_MINUTES} minutes"
            else:
                duration_str = self.get_last_login().get_duration_hm()
                self._log_out()
                
                daily_total = self.num_hours_today_hm()
                weekly_total = self.num_hours_this_week_hm()
                
                msg = (
                    f"{username} Logged out at {now_str} after {duration_str}<br>"
                    f"Daily total: {daily_total}<br>"
                    f"Weekly total (Sun-Sat): {weekly_total}"
                )
                good_result = True
        else:
            new_attendance = self._log_in()
            if CROSS_POST_LOGINS:  # pragma: no cover
                from attendance.models.sheets_backend import GoogleSheetsBackend

                sheets_backend = GoogleSheetsBackend()
                sheets_backend.signin(new_attendance)

            msg = f"{username} Logged in at {now_str}"
            good_result = True

        return msg, good_result

    def num_hours_today_hm(self) -> str:
        """Return total hours for the current calendar day as 'H hrs M min'."""
        now = timezone.now()
        start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
        attendance_query = self._get_attendance_set().filter(time_in__gte=start_of_day)
        total_delta = sum(
            [x.get_duration() for x in attendance_query],
            datetime.timedelta(),
        )
        total_seconds = int(total_delta.total_seconds())
        if total_seconds < 0:
            total_seconds = 0
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        return f"{hours} hrs {minutes} min"

    def num_hours_this_week_hm(self) -> str:
        """Return total hours for the current week (Sunday to Saturday) as 'H hrs M min'."""
        now = timezone.now()
        # weekday() returns 0 for Monday, 6 for Sunday.
        # We want Sunday to be the start (0 or 7 depending on logic).
        # In Python's weekday: Mon=0, Tue=1, Wed=2, Thu=3, Fri=4, Sat=5, Sun=6
        # If today is Sunday (6), we want days_since_sunday = 0
        # If today is Monday (0), we want days_since_sunday = 1
        days_since_sunday = (now.weekday() + 1) % 7
        start_of_week = (now - datetime.timedelta(days=days_since_sunday)).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        attendance_query = self._get_attendance_set().filter(time_in__gte=start_of_week)
        total_delta = sum(
            [x.get_duration() for x in attendance_query],
            datetime.timedelta(),
        )
        total_seconds = int(total_delta.total_seconds())
        if total_seconds < 0:
            total_seconds = 0
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        return f"{hours} hrs {minutes} min"

    def _attendance_filter(self):
        query_dict = get_filter_attendance_by_date_range_query()
        attendance_query = self._get_attendance_set().filter(**query_dict)
        return attendance_query

    def num_meetings(self):
        attendance_query = self._attendance_filter()
        return len(attendance_query)

    def num_hours(self):
        attendance_query = self._attendance_filter()
        total_time = sum(
            [x.get_duration() for x in attendance_query],
            datetime.timedelta(),
        )
        return total_time.total_seconds() / 3600

    def num_hours_hm(self) -> str:
        """Return total hours as 'H hrs M min' for the filtered attendance range."""
        attendance_query = self._attendance_filter()
        total_delta = sum(
            [x.get_duration() for x in attendance_query],
            datetime.timedelta(),
        )
        total_seconds = int(total_delta.total_seconds())
        if total_seconds < 0:
            total_seconds = 0
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        return f"{hours} hrs {minutes} min"

    def _log_out(self):
        last_login = self.get_last_login()
        last_login.time_out = timezone.now()
        last_login.save()

        if CROSS_POST_LOGINS:  # pragma: no cover
            from attendance.models.sheets_backend import GoogleSheetsBackend

            sheets_backend = GoogleSheetsBackend()
            sheets_backend.signout(last_login)

    @abc.abstractmethod
    def _get_attendance_set(self):  # pragma: no cover
        raise NotImplementedError()

    @abc.abstractmethod
    def _log_in(self):  # pragma: no cover
        raise NotImplementedError()

    @abc.abstractmethod
    def _full_name(self) -> str:  # pragma: no cover
        raise NotImplementedError()


class AttendanceMixin(models.Model):
    time_in = models.DateTimeField("Time In")
    time_out = models.DateTimeField("Time Out", null=True)

    def get_duration(self):
        out = self.time_out or self.time_in + datetime.timedelta(hours=0)
        return out - self.time_in

    def get_duration_hm(self) -> str:
        """Return duration as 'H hrs M min' without seconds."""
        delta = self.get_duration()
        total_seconds = int(delta.total_seconds())
        if total_seconds < 0:
            total_seconds = 0
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        return f"{hours} hrs {minutes} min"

    class Meta:
        abstract = True
