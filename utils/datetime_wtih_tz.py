from datetime import datetime
from zoneinfo import ZoneInfo


def get_current_local_datetime():
    return datetime.now(tz=ZoneInfo("Asia/Jakarta"))

def get_current_local_date():
    return get_current_local_datetime().date()

def get_current_local_time():
    return get_current_local_datetime().timetz()