from django.utils import timezone

from attendance.models.year import GOS_SEASON_YEAR
from attendance.models.y2025.date_ranges import *
from attendance.models.y2026.date_ranges import *

DATE_RANGES = {}

if GOS_SEASON_YEAR == 2025:
    DATE_RANGES["All Season"] = (fall_season2024_start, None)
    DATE_RANGES["Fall Season"] = (fall_season2024_start, fall_season2024_end)
    DATE_RANGES["FTC Season"] = (ftc_season2024_start, ftc_season2024_end)
    DATE_RANGES["FRC Season"] = (frc_season2025_start, frc_season2025_end)
elif GOS_SEASON_YEAR == 2026:
    DATE_RANGES["All Season"] = (fall_season2025_start, None)
    DATE_RANGES["Fall Season"] = (fall_season2025_start, fall_season2025_end)
    DATE_RANGES["FTC Season"] = (ftc_season2025_start, ftc_season2025_end)
    DATE_RANGES["FRC Season"] = (frc_season2026_start, frc_season2026_end)


def get_date_range():
    start_date, end_date = DATE_RANGES["All Season"]
    now = timezone.now()
    if end_date is None:
        end_date = timezone.now()
    elif end_date > now:
        end_date = now

    return start_date, end_date


def get_filter_attendance_by_date_range_query():
    start_date, end_date = get_date_range()
    query_dict = dict()
    if start_date:
        query_dict["time_in__gt"] = start_date
    if end_date:
        query_dict["time_in__lt"] = end_date
    return query_dict
