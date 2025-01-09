import datetime

from django.test import TestCase
from django.utils import timezone

from attendance.models import GosAttendance, GosStudent


# Create your tests here.
class AttendanceTest(TestCase):

    def test_log_in(self):
        t = timezone.now()

        student = GosStudent.objects.create(
            rfid=3504, first_name="Test", last_name="User"
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
            rfid=3504, first_name="Test", last_name="User"
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
