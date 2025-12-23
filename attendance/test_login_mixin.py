import datetime

from django.test import TestCase
from django.utils import timezone
from unittest.mock import patch

from attendance.models import GosAttendance, GosStudent, GosGradeLevel


class AttendanceTest(TestCase):

    def test_log_in(self):
        t = timezone.now()

        student = GosStudent.objects.create(
            rfid=3504, first_name="Test", last_name="User", grade=GosGradeLevel.EIGHTH
        )
        self.assertFalse(student.is_logged_in())

        # Log the student in
        attendance = GosAttendance.objects.create(student=student, time_in=t)
        self.assertTrue(student.is_logged_in())

        # Log the student out
        attendance.time_out = t + datetime.timedelta(1)
        attendance.save()
        self.assertFalse(student.is_logged_in())

    def test_log_in_with_partial_attendance(self):
        student = GosStudent.objects.create(
            rfid=3504, first_name="Test", last_name="User", grade=GosGradeLevel.EIGHTH
        )
        self.assertFalse(student.is_logged_in())

        t = timezone.now()

        # Create an in-only log that is more than our threshold
        GosAttendance.objects.create(
            student=student, time_in=t - datetime.timedelta(1), time_out=None
        )
        self.assertFalse(student.is_logged_in())

        # Create a recent login
        GosAttendance.objects.create(
            student=student, time_in=t - datetime.timedelta(minutes=1), time_out=None
        )
        self.assertTrue(student.is_logged_in())

    def test_debounce_login(self):
        student = GosStudent.objects.create(
            rfid=3504, first_name="Test", last_name="User", grade=GosGradeLevel.EIGHTH
        )
        self.assertFalse(student.is_logged_in())

        now = timezone.now()
        GosAttendance.objects.create(
            student=student, time_in=now - datetime.timedelta(seconds=1), time_out=None
        )
        msg, is_good = student.handle_signin_attempt()

        self.assertTrue("Test User tapped twice in" in msg)
        self.assertFalse(is_good)

    def test_num_hours_today_hm(self):
        student = GosStudent.objects.create(
            rfid=3505, first_name="Test", last_name="User2", grade=GosGradeLevel.EIGHTH
        )
        now = timezone.now()
        # Create an attendance entry for today
        GosAttendance.objects.create(
            student=student,
            time_in=now.replace(hour=10, minute=0, second=0, microsecond=0),
            time_out=now.replace(hour=12, minute=30, second=0, microsecond=0),
        )
        self.assertEqual(student.num_hours_today_hm(), "2 hrs 30 min")

    def test_num_hours_this_week_hm(self):
        student = GosStudent.objects.create(
            rfid=3506, first_name="Test", last_name="User3", grade=GosGradeLevel.EIGHTH
        )
        now = timezone.now()
        # Find some day this week (e.g. last Monday)
        days_since_sunday = (now.weekday() + 1) % 7
        last_sunday = (now - datetime.timedelta(days=days_since_sunday)).replace(
            hour=10, minute=0
        )

        GosAttendance.objects.create(
            student=student,
            time_in=last_sunday,
            time_out=last_sunday + datetime.timedelta(hours=3, minutes=15),
        )
        self.assertEqual(student.num_hours_this_week_hm(), "3 hrs 15 min")

    def test_num_hours_hm_and_meetings(self):
        student = GosStudent.objects.create(
            rfid=3507, first_name="Test", last_name="User4", grade=GosGradeLevel.EIGHTH
        )
        # Mock DATE_RANGES to include our test attendance
        tz = timezone.get_current_timezone()
        start = datetime.datetime(2025, 1, 1, tzinfo=tz)
        end = datetime.datetime(2025, 12, 31, tzinfo=tz)

        with patch(
            "attendance.models.date_ranges.get_date_range", return_value=(start, end)
        ):
            GosAttendance.objects.create(
                student=student,
                time_in=datetime.datetime(2025, 2, 1, 10, 0, tzinfo=tz),
                time_out=datetime.datetime(2025, 2, 1, 14, 0, tzinfo=tz),
            )
            GosAttendance.objects.create(
                student=student,
                time_in=datetime.datetime(2025, 2, 2, 10, 0, tzinfo=tz),
                time_out=datetime.datetime(2025, 2, 2, 11, 45, tzinfo=tz),
            )

            self.assertEqual(student.num_meetings(), 2)
            self.assertEqual(student.num_hours(), 5.75)
            self.assertEqual(student.num_hours_hm(), "5 hrs 45 min")
