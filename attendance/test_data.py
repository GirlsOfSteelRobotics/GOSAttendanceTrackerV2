import datetime

from django.utils import timezone

from attendance.models import (
    FieldBuilder,
    FieldBuilderAttendance,
    GosAttendance,
    GosStudent,
    ScraVisitor,
    ScraVisitorAttendance,
)


def create_gos_student_test_data():

    student1 = GosStudent.objects.create(rfid=1, first_name="Test", last_name="User1")
    student2 = GosStudent.objects.create(rfid=2, first_name="Test", last_name="User2")
    student3 = GosStudent.objects.create(rfid=3, first_name="Test", last_name="User3")

    now = timezone.now()

    meeting_one_date = now - datetime.timedelta(days=10)
    meeting_two_date = meeting_one_date + datetime.timedelta(days=3)
    meeting_three_date = now + datetime.timedelta(hours=-2.29)

    GosAttendance.objects.create(
        student=student1,
        time_in=meeting_one_date,
        time_out=meeting_one_date + datetime.timedelta(hours=2.5),
    )
    GosAttendance.objects.create(student=student1, time_in=meeting_two_date)

    GosAttendance.objects.create(student=student2, time_in=meeting_three_date)

    all_students = [student1, student2, student3]

    return all_students


def create_scra_test_data():
    user1 = ScraVisitor.objects.create(full_name="191 - 1", team_number=191)
    user2 = ScraVisitor.objects.create(full_name="191 - 2", team_number=191)
    user3 = ScraVisitor.objects.create(full_name="191 - 3", team_number=191)
    user4 = ScraVisitor.objects.create(full_name="229 - 1", team_number=229)
    user5 = ScraVisitor.objects.create(full_name="229 - 2", team_number=229)
    user6 = ScraVisitor.objects.create(full_name="174 - 1", team_number=174)

    now = timezone.now()

    meeting_one_date = now - datetime.timedelta(days=10)
    meeting_two_date = meeting_one_date + datetime.timedelta(days=3)
    meeting_three_date = now + datetime.timedelta(hours=-2.29)

    ScraVisitorAttendance.objects.create(
        scra_visitor=user1,
        time_in=meeting_one_date,
        time_out=meeting_one_date + datetime.timedelta(hours=2.5),
    )
    ScraVisitorAttendance.objects.create(scra_visitor=user1, time_in=meeting_two_date)
    ScraVisitorAttendance.objects.create(scra_visitor=user2, time_in=meeting_two_date)

    ScraVisitorAttendance.objects.create(scra_visitor=user4, time_in=meeting_three_date)

    all_users = [user1, user2, user3, user4, user5, user6]
    return all_users


def create_field_builder_test_data():
    user1 = FieldBuilder.objects.create(full_name="Field Builder 1")
    user2 = FieldBuilder.objects.create(full_name="Field Builder 2")
    user3 = FieldBuilder.objects.create(full_name="Field Builder 3")

    now = timezone.now()

    meeting_one_date = now - datetime.timedelta(days=10)
    meeting_two_date = meeting_one_date + datetime.timedelta(days=3)
    meeting_three_date = now + datetime.timedelta(hours=-2.29)

    FieldBuilderAttendance.objects.create(
        field_builder=user1,
        time_in=meeting_one_date,
        time_out=meeting_one_date + datetime.timedelta(hours=2.5),
    )
    FieldBuilderAttendance.objects.create(field_builder=user1, time_in=meeting_two_date)
    FieldBuilderAttendance.objects.create(field_builder=user2, time_in=meeting_two_date)

    FieldBuilderAttendance.objects.create(
        field_builder=user3, time_in=meeting_three_date
    )

    all_users = [user1, user2, user3]
    return all_users
