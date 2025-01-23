from django.urls import path

from .views import gos
from .views import field_builders
from .views import scra
from .views import top_level

urlpatterns = [
    path("", top_level.IndexView.as_view(), name="index"),
    path("manifest/", top_level.ActiveManifest.as_view(), name="active_manifest"),
    path("gos/", gos.GosStudentSummaryView.as_view(), name="gos_student_summary"),
    path("gos/signin", gos.gos_signin, name="gos_signin"),
    path(
        "gos/log_attendance_rfid",
        gos.gos_log_attendance_rfid,
        name="gos_log_attendance_rfid",
    ),
    path(
        "gos/log_attendance_name",
        gos.gos_log_attendance_name,
        name="gos_log_attendance_name",
    ),
    path(
        "gos/<int:rfid>/",
        gos.GosStudentDetailView.as_view(),
        name="gos_student_detail",
    ),
    # SCRA
    path("scra/signin", scra.ScraSignin.as_view(), name="scra_signin"),
    path(
        "scra/log_attendance",
        scra.scra_log_attendance,
        name="scra_log_attendance",
    ),
    path(
        "scra",
        scra.ScraVisitorList.as_view(),
        name="scra_visitor_list",
    ),
    # Field Builders
    path(
        "field_builders",
        field_builders.FieldBuilderList.as_view(),
        name="field_builders_list",
    ),
    path(
        "field_builders/signin",
        field_builders.FieldBuildersSignin.as_view(),
        name="field_builders_signin",
    ),
    path(
        "field_builders/log_attendance",
        field_builders.field_builders_log_attendance,
        name="field_builders_log_attendance",
    ),
]
