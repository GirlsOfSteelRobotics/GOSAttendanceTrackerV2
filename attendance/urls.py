from django.urls import path

from . import views

urlpatterns = [
    path("", views.IndexView.as_view(), name="index"),
    path("manifest/", views.ActiveManifest.as_view(), name="active_manifest"),
    path("gos/", views.GosStudentSummaryView.as_view(), name="gos_student_summary"),
    path("gos/signin", views.gos_signin, name="gos_signin"),
    path(
        "gos/log_attendance_rfid",
        views.gos_log_attendance_rfid,
        name="gos_log_attendance_rfid",
    ),
    path(
        "gos/log_attendance_name",
        views.gos_log_attendance_name,
        name="gos_log_attendance_name",
    ),
    path(
        "gos/<int:rfid>/",
        views.GosStudentDetailView.as_view(),
        name="gos_student_detail",
    ),
]
