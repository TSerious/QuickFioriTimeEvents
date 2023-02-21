import datetime
from enum import Enum

class Formats(Enum):
    d_m_y_H_M_S:str = '%d/%m/%y %H:%M:%S'
    H_M_S:str = '%H:%M:%S'
    HMS:str = '%H%M%S'
    d_m_y:str = '%d/%m/%y'
    dmy:str = '%d.%m.%y'
    dmy_H_M_S:str = '%d.%m.%y %H:%M:%S'
    DMY:str = '%d.%m.%Y'
    DMY_H_M_S:str = '%d.%m.%Y %H:%M:%S'

def to_datetime(dateTime:str, format:Formats|None = None) -> datetime.datetime:
    if format == None:
        format = Formats.d_m_y_H_M_S
    
    if len(dateTime) <= 0:
        return None

    return datetime.datetime.strptime(dateTime, format.value)

def to_string(dateTime:datetime, format:Formats|None = None) -> str:
    if dateTime == None:
        return ''

    if format == None:
        format = Formats.d_m_y_H_M_S

    return datetime.datetime.strftime(dateTime, format.value)

def timedelta_to_string(delta:datetime.timedelta) -> str:
    totalSeconds = delta.total_seconds()

    hourSeconds = totalSeconds - (totalSeconds % 3600)
    hours = int(hourSeconds / 3600)

    minuteSeconds = (totalSeconds - hourSeconds) - ((totalSeconds - hourSeconds) % 60)
    minutes = int(minuteSeconds / 60)

    seconds = int(totalSeconds - minuteSeconds - hourSeconds)

    return "{:>02}".format(str(hours)) + ":" + "{:>02}".format(str(minutes)) + ":" + "{:>02}".format(str(seconds))