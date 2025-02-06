from django.test import TestCase
from django.urls import reverse

from attendance.test_data import (
    create_gos_student_test_data,
    create_field_builder_test_data,
    create_scra_test_data,
)


def create_test_data():
    create_gos_student_test_data()
    create_field_builder_test_data()
    create_scra_test_data()


class IndexViewTest(TestCase):
    def test_page_load(self):
        create_test_data()

        response = self.client.get(reverse("index"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(9, len(response.context["calendar_events"]))


class ActiveManifestTest(TestCase):
    def test_page_load(self):
        create_test_data()

        response = self.client.get(reverse("active_manifest"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(1, len(response.context["gos_students"]))
        self.assertEqual(1, len(response.context["scra_visitors"]))
        self.assertEqual(1, len(response.context["field_builders"]))
