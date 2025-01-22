# Register your models here.
from django.contrib import admin

from attendance.models import (
    ScraVisitor,
    FieldBuilder,
    FieldBuilderAttendance,
    GosAttendance,
    ScraVisitorAttendance,
)
from attendance.models.gos import GosStudent

admin.site.register(GosStudent)
admin.site.register(GosAttendance)
admin.site.register(ScraVisitor)
admin.site.register(ScraVisitorAttendance)
admin.site.register(FieldBuilder)
admin.site.register(FieldBuilderAttendance)
