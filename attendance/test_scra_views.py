
from django.test import TestCase
from django.urls import reverse

from attendance.models import (
    ScraVisitor,
)
from attendance.models.mixins import set_cross_post_login
from attendance.test_data import create_scra_test_data

# Don't post test results to the google sheets backup
set_cross_post_login(False)


class ScraSigninPageTest(TestCase):
    def test_page_load(self):
        create_scra_test_data()

        response = self.client.get(reverse("scra_signin"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '"174":["174 - 1", ]')
        self.assertContains(response, '"191":["191 - 1", "191 - 2", "191 - 3", ]')
        self.assertContains(response, '"229":["229 - 1", "229 - 2", ]')

        teams = response.context["teams"]
        self.assertEqual(len(teams), 3)

        self.assertEqual(3, len(teams[191]))
        self.assertQuerySetEqual(
            teams[191], ScraVisitor.objects.filter(team_number=191), ordered=False
        )

        self.assertEqual(1, len(teams[174]))
        self.assertQuerySetEqual(
            teams[174], ScraVisitor.objects.filter(team_number=174), ordered=False
        )

        self.assertEqual(2, len(teams[229]))
        self.assertQuerySetEqual(
            teams[229], ScraVisitor.objects.filter(team_number=229), ordered=False
        )


class ScraLogAttendanceTest(TestCase):
    def test_empty_name(self):
        response = self.client.post(
            reverse("scra_log_attendance"), dict(team_number=191, full_name="")
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("scra_signin"))
        self.assertEqual(
            "You must enter a full name.", self.client.session["result_msg"]
        )
        self.assertFalse(self.client.session["good_result"])

    def test_signin_existing_visitor(self):
        all_visitors = create_scra_test_data()
        visitor_ut = all_visitors[0]

        # Check attendance before the signin attempt
        self.assertEqual(2, len(visitor_ut.scravisitorattendance_set.all()))

        response = self.client.post(
            reverse("scra_log_attendance"),
            dict(team_number=visitor_ut.team_number, full_name=visitor_ut.full_name),
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("scra_signin"))
        self.assertEqual("191 - 1 Logged in", self.client.session["result_msg"])
        self.assertTrue(self.client.session["good_result"])

        # Verify there is a new attendance entry
        self.assertEqual(3, len(visitor_ut.scravisitorattendance_set.all()))

    def test_signin_new_visitor(self):
        response = self.client.post(
            reverse("scra_log_attendance"),
            dict(team_number=254, full_name="New Visitor"),
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("scra_signin"))
        self.assertEqual(
            "New Visitor Logged in. As a new visitor, please make sure you have filled out the CMU forms",
            self.client.session["result_msg"],
        )
        self.assertTrue(self.client.session["good_result"])


class ScraVisitorListTest(TestCase):
    def test_calendar_events(self):
        create_scra_test_data()

        response = self.client.get(reverse("scra_visitor_list"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(3, len(response.context["teams"]))
        self.assertEqual(3, len(response.context["calendar_events"]))

        event = response.context["calendar_events"][0]
        self.assertEqual("1 Team 191", event.title)
        self.assertTrue(event.show_as_all_day)

        event = response.context["calendar_events"][1]
        self.assertEqual("2 Team 191", event.title)
        self.assertTrue(event.show_as_all_day)

        event = response.context["calendar_events"][2]
        self.assertEqual("1 Team 229", event.title)
        self.assertTrue(event.show_as_all_day)
