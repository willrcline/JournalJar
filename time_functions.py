from datetime import datetime
import pytz

def to_utc(time, time_zone):
    utc = pytz.timezone('UTC')
    now = utc.localize(datetime.utcnow())
    #timezone of choice
    tz = pytz.timezone(time_zone)

    #create timestamp in timezone of choice
    local_time = now.astimezone(tz)

    #now that I have an object with the right properties, replace the hour and minute to what you need it to be
    h = int(time.split(":")[0])
    m = int(time.split(":")[1])
    local_time = local_time.replace(hour=h)
    local_time = local_time.replace(minute=m)

    local_time = local_time.astimezone(utc)
    return local_time