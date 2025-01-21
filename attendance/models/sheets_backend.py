import gspread
import logging
import os
import pytz
from django.utils import timezone


SPREADSHEET_KEY = "1ztlyayX_A59oDQQsRPfWNKSZ-efkdWKgML-J9WtB66s"


class GoogleSheetsBackend:
    def __init__(self):
        logging.info("Connecting to sheets")
        gc = gspread.service_account(filename=os.path.abspath("credentials.json"))
        self.spreadsheet = gc.open_by_key(SPREADSHEET_KEY)

    def format_time(self, current_time) -> str:
        utc = current_time.replace(tzinfo=pytz.UTC)
        in_local = utc.astimezone(timezone.get_current_timezone())
        return in_local.strftime("%m/%d/%y %I:%M %p")

    def gos_signin(self, timestamp, rfid, full_name):
        sheet_tab = self.spreadsheet.worksheet("GoS Attendance")

        row_contents = [self.format_time(timestamp), rfid, full_name, "General Meeting"]
        sheet_tab.append_row(row_contents, value_input_option="USER_ENTERED")

    def gos_signout(self, timestamp, full_name):
        sheet_tab = self.spreadsheet.worksheet("GoS Attendance")
        cell_list = sheet_tab.findall(full_name)
        if cell_list:
            last_cell = cell_list[-1]
            last_row_num = last_cell.row
            sheet_tab.update_cell(last_row_num, 5, self.format_time(timestamp))
