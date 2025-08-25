import gspread
import logging
import os
import pytz
from django.utils import timezone

from attendance.models import (
    GosAttendance,
    ScraVisitorAttendance,
    FieldBuilderAttendance,
)

# SPREADSHEET_KEY = "1ztlyayX_A59oDQQsRPfWNKSZ-efkdWKgML-J9WtB66s" # 24-25
SPREADSHEET_KEY = "1T-rXZDCy05_uNRha7ZyMda8Cs9b6YXDQLG4KUIL9tQY"  # 25-26


def format_time(current_time) -> str:
    utc = current_time.replace(tzinfo=pytz.UTC)
    in_local = utc.astimezone(timezone.get_current_timezone())
    return in_local.strftime("%m/%d/%y %I:%M:%S %p")


class GoogleSheetsBackend:
    GOS_ATTENDANCE_TAB = "GoS Attendance"
    SCRA_ATTENDANCE_TAB = "SCRA Visitor Attendance"
    FIELD_BUILDER_TAB = "Field Builder Attendance"

    def __init__(self):
        logging.info("Connecting to sheets")
        gc = gspread.service_account(filename=os.path.abspath("credentials.json"))
        self.spreadsheet = gc.open_by_key(SPREADSHEET_KEY)

    def signin(
        self, attendance: GosAttendance | ScraVisitorAttendance | FieldBuilderAttendance
    ):
        if isinstance(attendance, GosAttendance):
            self.gos_signin(attendance)
        elif isinstance(attendance, ScraVisitorAttendance):
            self.scra_signin(attendance)
        elif isinstance(attendance, FieldBuilderAttendance):
            self.field_builder_signin(attendance)
        else:
            raise Exception("Invalid attendance")

    def signout(
        self, attendance: GosAttendance | ScraVisitorAttendance | FieldBuilderAttendance
    ):
        if isinstance(attendance, GosAttendance):
            self.gos_signout(attendance)
        elif isinstance(attendance, ScraVisitorAttendance):
            self.scra_signout(attendance)
        elif isinstance(attendance, FieldBuilderAttendance):
            self.field_builder_signout(attendance)
        else:
            raise Exception("Invalid attendance")

    def scra_signin(self, attendance: ScraVisitorAttendance):
        row_contents = [
            attendance.scra_visitor.team_number,
            attendance.scra_visitor.full_name,
            format_time(attendance.time_in),
        ]
        sheet_tab = self.spreadsheet.worksheet(self.SCRA_ATTENDANCE_TAB)
        sheet_tab.append_row(row_contents, value_input_option="USER_ENTERED")

    def scra_signout(self, attendance: ScraVisitorAttendance):
        print("SCRA signout, ", attendance)
        self.__signout_helper(
            attendance.scra_visitor.full_name,
            self.SCRA_ATTENDANCE_TAB,
            4,
            attendance.time_out,
        )

    def gos_signin(self, attendance: GosAttendance):
        row_contents = [
            attendance.student.full_name(),
            "General Meeting",
            attendance.student.rfid,
            format_time(attendance.time_in),
        ]
        sheet_tab = self.spreadsheet.worksheet(self.GOS_ATTENDANCE_TAB)
        sheet_tab.append_row(row_contents, value_input_option="USER_ENTERED")

    def gos_signout(self, attendance: GosAttendance):
        self.__signout_helper(
            attendance.student.full_name(),
            self.GOS_ATTENDANCE_TAB,
            5,
            attendance.time_out,
        )

    def field_builder_signin(self, attendance: FieldBuilderAttendance):
        row_contents = [
            attendance.field_builder.full_name,
            format_time(attendance.time_in),
        ]
        sheet_tab = self.spreadsheet.worksheet(self.FIELD_BUILDER_TAB)
        sheet_tab.append_row(row_contents, value_input_option="USER_ENTERED")

    def field_builder_signout(self, attendance: FieldBuilderAttendance):
        self.__signout_helper(
            attendance.field_builder.full_name,
            self.FIELD_BUILDER_TAB,
            3,
            attendance.time_out,
        )

    def __signout_helper(
        self, full_name: str, tab_name: str, date_out_index, timestamp
    ):
        sheet_tab = self.spreadsheet.worksheet(tab_name)
        cell_list = sheet_tab.findall(full_name)
        if cell_list:
            last_cell = cell_list[-1]
            last_row_num = last_cell.row
            sheet_tab.update_cell(last_row_num, date_out_index, format_time(timestamp))
