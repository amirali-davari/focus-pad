from random import randint
from jdatetime import datetime, time, timedelta

def formated_string_date(date_obj):
    day = date_obj.day
    if 4 <= day <= 20 or 24 <= day <= 30:
        suffix = "th"
    else:
        suffix = ["st", "nd", "rd"][day % 10 - 1]
    return date_obj.strftime(f'%A, {day}{suffix} of %B %Y')

def formatted_string_time(minutes):
    hours, minutes = divmod(minutes, 60)
    parts = []
    if hours:
        parts.append(f"{hours} hour{'s' if hours != 1 else ''}")
    if minutes:
        parts.append(f"{minutes} minute{'s' if minutes != 1 else ''}")
    if not parts:
        return "0 minutes"
    return " and ".join(parts)

def get_info(date_obj):
    # Search the database and return : focus_time, goal (in minutes)
    return randint(50, 70), randint(70, 90)

def time_left_til_midnight():
    dt = datetime.now()
    tomorrow = dt + timedelta(days=1)
    delta = datetime.combine(tomorrow, time(0,0)) - dt
    return delta.seconds // 60 + 1

def get_month_length(date_obj):
    return (date_obj.replace(year=date_obj.year + (date_obj.month == 12), month=date_obj.month % 12 + 1, day=1)- timedelta(days=1)).day
