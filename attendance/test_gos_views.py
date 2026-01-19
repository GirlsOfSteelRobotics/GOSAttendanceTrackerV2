from django.test import TestCase
from django.urls import reverse

from attendance.models.mixins import set_cross_post_login
from attendance.test_data import create_gos_student_test_data

# Don't post test results to the google sheets backup
set_cross_post_login(False)


class GosStudentSummaryTests(TestCase):

    def test_no_students(self):
        response = self.client.get(reverse("gos_student_summary"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No students available")
        self.assertQuerySetEqual(response.context["object_list"], [])

    def test_table(self):
        all_students = create_gos_student_test_data()

        response = self.client.get(reverse("gos_student_summary"))
        self.assertEqual(response.status_code, 200)
        self.assertQuerySetEqual(
            response.context["object_list"], all_students, ordered=False
        )


class GosStudentDetailTest(TestCase):
    def test_invalid_student(self):
        response = self.client.get(
            reverse("gos_student_detail", kwargs=dict(rfid=12345))
        )
        self.assertEqual(response.status_code, 404)

    def test_valid_student(self):
        all_students = create_gos_student_test_data()
        student_ut = all_students[0]

        response = self.client.get(
            reverse("gos_student_detail", kwargs=dict(rfid=student_ut.rfid))
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response, f"<h1>{student_ut.first_name} {student_ut.last_name}</h1>"
        )
        self.assertEqual(2, len(response.context["object"].gosattendance_set.all()))


class GosSigninCombinedTest(TestCase):
    def test_empty_query(self):
        response = self.client.post(reverse("gos_log_attendance"), dict(search_query=""))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            "Please tap your RFID keyfob or enter your full name.",
            self.client.session["result_msg"],
        )
        self.assertFalse(self.client.session["good_result"])

    def test_invalid_rfid(self):
        response = self.client.post(reverse("gos_log_attendance"), dict(search_query="191"))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            "No student found with RFID 191", self.client.session["result_msg"]
        )
        self.assertFalse(self.client.session["good_result"])

    def test_valid_rfid_signin(self):
        all_students = create_gos_student_test_data()
        student_ut = all_students[0]

        # Check attendance before the signin attempt
        self.assertEqual(2, len(student_ut.gosattendance_set.all()))

        response = self.client.post(
            reverse("gos_log_attendance"), dict(search_query=str(student_ut.rfid))
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("gos_signin"))
        self.assertIn("Test User1 Logged in at", self.client.session["result_msg"])
        self.assertTrue(self.client.session["good_result"])

        # Verify there is a new attendance entry
        self.assertEqual(3, len(student_ut.gosattendance_set.all()))

    def test_partial_name(self):
        response = self.client.post(
            reverse("gos_log_attendance"), dict(search_query="Prince")
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            "Invalid student name Prince, could not split the name into two parts (First Last)",
            self.client.session["result_msg"],
        )
        self.assertFalse(self.client.session["good_result"])

    def test_invalid_name(self):
        response = self.client.post(
            reverse("gos_log_attendance"), dict(search_query="Fake Student")
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            "Invalid student name Fake Student", self.client.session["result_msg"]
        )
        self.assertFalse(self.client.session["good_result"])

    def test_valid_name_signin(self):
        all_students = create_gos_student_test_data()
        student_ut = all_students[0]

        # Check attendance before the signin attempt
        self.assertEqual(2, len(student_ut.gosattendance_set.all()))

        response = self.client.post(
            reverse("gos_log_attendance"), dict(search_query=student_ut.full_name())
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("gos_signin"))
        self.assertIn("Test User1 Logged in at", self.client.session["result_msg"])
        self.assertTrue(self.client.session["good_result"])

        # Verify there is a new attendance entry
        self.assertEqual(3, len(student_ut.gosattendance_set.all()))

    def test_signout_rfid(self):
        all_students = create_gos_student_test_data()
        student_ut = all_students[1]

        # Check attendance before the signin attempt
        self.assertEqual(1, len(student_ut.gosattendance_set.all()))
        self.assertTrue(student_ut.is_logged_in())

        response = self.client.post(
            reverse("gos_log_attendance"), dict(search_query=str(student_ut.rfid))
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("gos_signin"))
        self.assertIn("Test User2 Logged out at", self.client.session["result_msg"])
        self.assertTrue(self.client.session["good_result"])

        self.assertEqual(1, len(student_ut.gosattendance_set.all()))
        self.assertFalse(student_ut.is_logged_in())

    def test_signout_name(self):
        all_students = create_gos_student_test_data()
        student_ut = all_students[1]

        # Check attendance before the signin attempt
        self.assertEqual(1, len(student_ut.gosattendance_set.all()))
        self.assertTrue(student_ut.is_logged_in())

        response = self.client.post(
            reverse("gos_log_attendance"), dict(search_query=student_ut.full_name())
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("gos_signin"))
        self.assertIn("Test User2 Logged out at", self.client.session["result_msg"])
        self.assertTrue(self.client.session["good_result"])

        self.assertEqual(1, len(student_ut.gosattendance_set.all()))
        self.assertFalse(student_ut.is_logged_in())


class GosSigninPageTest(TestCase):
    def test_page_load(self):
        response = self.client.get(reverse("gos_signin"))
        self.assertEqual(response.status_code, 200)
