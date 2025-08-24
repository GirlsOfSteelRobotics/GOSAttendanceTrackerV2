from attendance.models.y2025.gos import GosProgram2025, GosSubteam2025

year = 2025

if year == 2025:
    from attendance.models.y2025.field_builders import *  # noqa
    from attendance.models.y2025.gos import *  # noqa
    from attendance.models.y2025.scra import *  # noqa

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
