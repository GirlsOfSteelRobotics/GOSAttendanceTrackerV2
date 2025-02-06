
from django.test import TestCase
from django.urls import reverse

from attendance.models.mixins import set_cross_post_login
from attendance.test_data import create_field_builder_test_data

# Don't post test results to the google sheets backup
set_cross_post_login(False)


class FieldBuilderSigninPageTest(TestCase):
    def test_page_load(self):
        create_field_builder_test_data()

        response = self.client.get(reverse("field_builders_signin"))
        self.assertEqual(response.status_code, 200)
        field_builders = response.context["field_builders"]
        self.assertEqual(len(field_builders), 3)


class FieldBuilderLogAttendanceTest(TestCase):
    def test_empty_name(self):
        response = self.client.post(
            reverse("field_builders_log_attendance"),
            dict(team_number=191, full_name=""),
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("field_builders_signin"))
        self.assertEqual(
            "You must enter a full name.", self.client.session["result_msg"]
        )
        self.assertFalse(self.client.session["good_result"])

    def test_signin_existing_visitor(self):
        all_visitors = create_field_builder_test_data()
        visitor_ut = all_visitors[0]

        # Check attendance before the signin attempt
        self.assertEqual(2, len(visitor_ut.fieldbuilderattendance_set.all()))

        response = self.client.post(
            reverse("field_builders_log_attendance"),
            dict(full_name=visitor_ut.full_name),
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("field_builders_signin"))
        self.assertEqual("Field Builder 1 Logged in", self.client.session["result_msg"])
        self.assertTrue(self.client.session["good_result"])

        # Verify there is a new attendance entry
        self.assertEqual(3, len(visitor_ut.fieldbuilderattendance_set.all()))

    def test_signin_new_visitor(self):
        response = self.client.post(
            reverse("field_builders_log_attendance"),
            dict(team_number=254, full_name="New Visitor"),
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("field_builders_signin"))
        self.assertEqual(
            "New Visitor Logged in. As a new visitor, please make sure you have filled out the CMU forms",
            self.client.session["result_msg"],
        )
        self.assertTrue(self.client.session["good_result"])


class FieldBuildersListTest(TestCase):
    def test_calendar_events(self):
        create_field_builder_test_data()

        response = self.client.get(reverse("field_builders_list"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(3, len(response.context["field_builders"]))
        self.assertEqual(4, len(response.context["calendar_events"]))

        event = response.context["calendar_events"][0]
        self.assertEqual("Field Builder 1", event.title)
        self.assertFalse(event.show_as_all_day)

        event = response.context["calendar_events"][1]
        self.assertEqual("Field Builder 1", event.title)
        self.assertFalse(event.show_as_all_day)

        event = response.context["calendar_events"][2]
        self.assertEqual("Field Builder 2", event.title)
        self.assertFalse(event.show_as_all_day)

        event = response.context["calendar_events"][3]
        self.assertEqual("Field Builder 3", event.title)
        self.assertFalse(event.show_as_all_day)
