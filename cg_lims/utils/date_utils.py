from datetime import time, datetime as dt


def str_to_datetime(date: str) -> dt:
    """Convert str to datetime"""

    if date is None:
        return None
    return dt.strptime(date, "%Y-%m-%d")


def datetime2date(date: dt) -> dt.date:
    """Convert datetime.datetime to datetime.date"""

    if date is None:
        return None
    return dt(date.year, date.month, date.day)


def get_number_of_days(first_date: dt, second_date: dt) -> int:
    """Get number of days between different time stamps."""

    days = None
    if first_date and second_date:
        time_span = second_date - first_date
        days = time_span.days
    return days
