from datetime import datetime
from dateutil import tz

JST = tz.gettz('Asia/Tokyo')

def current_datetime():
    return datetime.now(JST)

def timestamp_to_datetime(timestamp):
    return datetime.fromtimestamp(timestamp, JST)

if __name__ == '__main__':
    print(current_datetime())
    current_date = current_datetime().date()
    date_str = datetime.strftime(current_date, "%Y%m%d")
