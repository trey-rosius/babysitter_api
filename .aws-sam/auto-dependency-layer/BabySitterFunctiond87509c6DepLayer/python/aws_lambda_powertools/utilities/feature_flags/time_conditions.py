from datetime import datetime, tzinfo
from typing import Dict, Optional

from dateutil.tz import gettz

from .schema import HOUR_MIN_SEPARATOR, TimeValues


def _get_now_from_timezone(timezone: Optional[tzinfo]) -> datetime:
    """
    Returns now in the specified timezone. Defaults to UTC if not present.
    At this stage, we already validated that the passed timezone string is valid, so we assume that
    gettz() will return a tzinfo object.
    """
    timezone = gettz("UTC") if timezone is None else timezone
    return datetime.now(timezone)


def compare_days_of_week(action: str, values: Dict) -> bool:
    timezone_name = values.get(TimeValues.TIMEZONE.value, "UTC")

    # %A = Weekday as locale’s full name.
    current_day = _get_now_from_timezone(gettz(timezone_name)).strftime("%A").upper()

    days = values.get(TimeValues.DAYS.value, [])
    return current_day in days


def compare_datetime_range(action: str, values: Dict) -> bool:
    timezone_name = values.get(TimeValues.TIMEZONE.value, "UTC")
    timezone = gettz(timezone_name)
    current_time: datetime = _get_now_from_timezone(timezone)

    start_date_str = values.get(TimeValues.START.value, "")
    end_date_str = values.get(TimeValues.END.value, "")

    # Since start_date and end_date doesn't include timezone information, we mark the timestamp
    # with the same timezone as the current_time. This way all the 3 timestamps will be on
    # the same timezone.
    start_date = datetime.fromisoformat(start_date_str).replace(tzinfo=timezone)
    end_date = datetime.fromisoformat(end_date_str).replace(tzinfo=timezone)
    return start_date <= current_time <= end_date


def compare_time_range(action: str, values: Dict) -> bool:
    timezone_name = values.get(TimeValues.TIMEZONE.value, "UTC")
    current_time: datetime = _get_now_from_timezone(gettz(timezone_name))

    start_hour, start_min = values.get(TimeValues.START.value, "").split(
        HOUR_MIN_SEPARATOR
    )
    end_hour, end_min = values.get(TimeValues.END.value, "").split(HOUR_MIN_SEPARATOR)

    start_time = current_time.replace(hour=int(start_hour), minute=int(start_min))
    end_time = current_time.replace(hour=int(end_hour), minute=int(end_min))

    if int(end_hour) < int(start_hour):
        # When the end hour is smaller than start hour, it means we are crossing a day's boundary.
        # In this case we need to assert that current_time is **either** on one side or the other side of the boundary
        #
        # ┌─────┐                                    ┌─────┐                                  ┌─────┐
        # │20.00│                                    │00.00│                                  │04.00│
        # └─────┘                                    └─────┘                                  └─────┘
        #    ───────────────────────────────────────────┬─────────────────────────────────────────▶
        #    ┌ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─  │ ┌ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─
        #                                             │ │                                        │
        #    │           either this area               │ │             or this area
        #                                             │ │                                        │
        #    └ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─  │ └ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─
        #                                               │

        return (start_time <= current_time) or (current_time <= end_time)
    else:
        # In normal circumstances, we need to assert **both** conditions
        return start_time <= current_time <= end_time
