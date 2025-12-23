import datetime
from django.test import TestCase
from unittest.mock import patch, MagicMock
from attendance.models import GosStudent, GosGradeLevel, GosAttendance
from attendance.models.sheets_backend import GoogleSheetsBackend


class SheetsBackendTest(TestCase):

    @patch("gspread.service_account")
    def test_signin_gos(self, mock_service_account):
        # Setup mocks
        mock_gc = MagicMock()
        mock_service_account.return_value = mock_gc
        mock_spreadsheet = MagicMock()
        mock_gc.open_by_key.return_value = mock_spreadsheet
        mock_sheet = MagicMock()
        mock_spreadsheet.worksheet.return_value = mock_sheet

        # Create test data
        student = GosStudent.objects.create(
            rfid=9999, first_name="Sheet", last_name="Test", grade=GosGradeLevel.SENIOR
        )
        attendance = GosAttendance.objects.create(
            student=student, time_in=datetime.datetime(2025, 1, 1, 12, 0)
        )

        # Call backend
        backend = GoogleSheetsBackend()
        backend.signin(attendance)

        # Verify calls
        mock_spreadsheet.worksheet.assert_called_with(
            GoogleSheetsBackend.GOS_ATTENDANCE_TAB
        )
        mock_sheet.append_row.assert_called_once()
        args, kwargs = mock_sheet.append_row.call_args
        row_contents = args[0]
        self.assertEqual(row_contents[0], "Sheet Test")
        self.assertEqual(row_contents[2], 9999)

    @patch("gspread.service_account")
    def test_signout_gos(self, mock_service_account):
        # Setup mocks
        mock_gc = MagicMock()
        mock_service_account.return_value = mock_gc
        mock_spreadsheet = MagicMock()
        mock_gc.open_by_key.return_value = mock_spreadsheet
        mock_sheet = MagicMock()
        mock_spreadsheet.worksheet.return_value = mock_sheet

        # Mock findall to return a cell
        mock_cell = MagicMock()
        mock_cell.row = 10
        mock_sheet.findall.return_value = [mock_cell]

        # Create test data
        student = GosStudent.objects.create(
            rfid=9998, first_name="Sheet", last_name="Out", grade=GosGradeLevel.SENIOR
        )
        attendance = GosAttendance.objects.create(
            student=student,
            time_in=datetime.datetime(2025, 1, 1, 12, 0),
            time_out=datetime.datetime(2025, 1, 1, 14, 0),
        )

        # Call backend
        backend = GoogleSheetsBackend()
        backend.signout(attendance)

        # Verify calls
        mock_spreadsheet.worksheet.assert_called_with(
            GoogleSheetsBackend.GOS_ATTENDANCE_TAB
        )
        mock_sheet.findall.assert_called_with("Sheet Out")
        mock_sheet.update_cell.assert_called_once()
        args, kwargs = mock_sheet.update_cell.call_args
        self.assertEqual(args[0], 10)  # last_row_num
        self.assertEqual(args[1], 5)  # date_out_index for GOS
