import datetime

import pytz

_tz = pytz.timezone("America/New_York")

fall_season2025_start = datetime.datetime(2025, 8, 25, tzinfo=_tz)
fall_season2025_end = datetime.datetime(2025, 12, 31, tzinfo=_tz)

ftc_season2025_start = datetime.datetime(2025, 8, 25, tzinfo=_tz)
ftc_season2025_end = datetime.datetime(2026, 3, 31, tzinfo=_tz)

frc_season2026_start = datetime.datetime(2026, 1, 1, tzinfo=_tz)
frc_season2026_end = datetime.datetime(2026, 4, 20, tzinfo=_tz)
