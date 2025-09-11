import pandas as pd

from typing import Optional
from attendance.models import GosStudent


def import_metadata():
    import_business_subteams()
    import_preseason_crews()


def _lookup_student(row) -> Optional[GosStudent]:
    name_parts = row["Name"].split(" ")
    lookup_query = {"first_name": name_parts[0]}
    if len(name_parts) > 1:
        lookup_query["last_name"] = name_parts[1]

    students = GosStudent.objects.filter(**lookup_query)
    if len(students) == 0:
        print(f"Could not lookup student matching query {lookup_query}")
        return None
    elif len(students) > 1:
        print(f"Multiple students matching query {lookup_query}")
        return None
    else:
        return students[0]


def import_business_subteams():
    filepath = r"attendance\tools\business_subteams.csv"

    contents = pd.read_csv(filepath)
    for index, row in contents.iterrows():
        team = row["Team"]
        student = _lookup_student(row)

        if student:
            student.business_subteam = team
            student.save()


def import_preseason_crews():
    filepath = r"attendance\tools\preseason_crews.csv"

    contents = pd.read_csv(filepath)
    for index, row in contents.iterrows():
        team = row["Team"]
        student = _lookup_student(row)

        if student:
            student.preseason_crew = team
            student.save()
