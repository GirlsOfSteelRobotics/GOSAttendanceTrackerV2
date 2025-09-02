import datetime

import pytz

_tz = pytz.timezone("America/New_York")

fall_season2024_start = datetime.datetime(2024, 9, 1, tzinfo=_tz)
fall_season2024_end = datetime.datetime(2025, 1, 1, tzinfo=_tz)

ftc_season2024_start = datetime.datetime(2024, 9, 1, tzinfo=_tz)
ftc_season2024_end = datetime.datetime(2025, 3, 27, tzinfo=_tz)

frc_season2025_start = datetime.datetime(2025, 1, 1, tzinfo=_tz)
frc_season2025_end = datetime.datetime(2025, 2, 26, tzinfo=_tz)
