from attendance.models.y2025.field_builders import *  # noqa
from attendance.models.y2025.gos import *  # noqa
from attendance.models.y2025.scra import *  # noqa
from attendance.models.y2026.field_builders import *  # noqa
from attendance.models.y2026.gos import *  # noqa
from attendance.models.y2026.scra import *  # noqa

year = 2026

if year == 2025:

    GosStudent = GosStudent2025
    GosAttendance = GosAttendance2025
    ScraVisitorAttendance = ScraVisitorAttendance2025
    ScraVisitor = ScraVisitor2025
    FieldBuilderAttendance = FieldBuilderAttendance2025
    FieldBuilder = FieldBuilder2025

    GosProgram = GosProgram2025
    GosSubteam = GosSubteam2025
    GosGradeLevel = GosGradeLevel2025
    GosPreseasonCrew = GosPreseasonCrew2025
elif year == 2026:
    GosStudent = GosStudent2026
    GosAttendance = GosAttendance2026
    ScraVisitorAttendance = ScraVisitorAttendance2026
    ScraVisitor = ScraVisitor2026
    FieldBuilderAttendance = FieldBuilderAttendance2026
    FieldBuilder = FieldBuilder2026

    GosProgram = GosProgram2026
    GosSubteam = GosSubteam2026
    GosGradeLevel = GosGradeLevel2026
    GosPreseasonCrew = GosPreseasonCrew2026
