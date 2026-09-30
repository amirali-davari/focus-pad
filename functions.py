from random import randint
from jdatetime import datetime, time, timedelta
import sqlite3
import csv

connection = sqlite3.connect("focuspad.db")

def startup():
    cursor = connection.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS days (
            date TEXT PRIMARY KEY,
            focus_time INTEGER NOT NULL,
            goal INTEGER NOT NULL
        )
    """)
    connection.commit()

def formatted_string_date(date_obj):
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
    cursor = connection.cursor()
    cursor.execute(
        "SELECT focus_time, goal FROM days WHERE date = ?",
        (str(date_obj),)
    )

    result = cursor.fetchone()

    return result

def time_left_til_midnight():
    dt = datetime.now()
    tomorrow = dt + timedelta(days=1)
    delta = datetime.combine(tomorrow, time(0,0)) - dt
    return delta.seconds // 60 + 1

def get_month_length(date_obj):
    return (date_obj.replace(year=date_obj.year + (date_obj.month == 12), month=date_obj.month % 12 + 1, day=1)- timedelta(days=1)).day

def get_all_database():
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM days")

    rows = cursor.fetchall()
    return rows

def replace_database(data):
    cursor = connection.cursor()
    cursor.execute("DELETE FROM days")

    cursor.executemany(
        "INSERT INTO days (date, focus_time, goal) VALUES (?, ?, ?)",
        data
    )

    connection.commit()

def reset_database():
    cursor = connection.cursor()
    cursor.execute("DELETE FROM days")

    connection.commit()

def dayEdit(date, newFocus, NewGoal):
    cursor = connection.cursor()
    cursor.execute("""
        INSERT INTO days (date, focus_time, goal)
        VALUES (?, ?, ?)
        ON CONFLICT(date) DO UPDATE SET
            focus_time = excluded.focus_time,
            goal = excluded.goal
    """, (str(date), newFocus, NewGoal))

    connection.commit()

def importCSV(file_path):
    data = []
    with open(file_path, 'r') as f:
        reader = csv.reader(f)
        if tuple(next(reader)) != ('date', 'focus_time', 'goal'):
            return False, 'BadHeaderError'
        for row in reader:
            try:
                data.append((row[0], int(row[1]), int(row[2])))
            except ValueError:
                return False, 'ValueError'

    cursor = connection.cursor()

    cursor.executemany("""
        INSERT INTO days (date, focus_time, goal)
        VALUES (?, ?, ?)
        ON CONFLICT(date) DO UPDATE SET
            focus_time = excluded.focus_time,
            goal = excluded.goal
    """, data)

    connection.commit()
    return True, None
