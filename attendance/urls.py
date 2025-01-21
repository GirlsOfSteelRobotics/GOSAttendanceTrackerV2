from django.urls import path

from .views import gos
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
]
