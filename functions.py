from random import randint
from jdatetime import datetime, time, timedelta, date
import sqlite3
import csv
from PySide6.QtCore import QElapsedTimer
import matplotlib.pyplot as plt

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

class StopwatchLogic:
    def __init__(self):
        self.elapsedTimer = QElapsedTimer()
        self.is_running = False
        self.time_passed = 0

    def start(self):
        if not self.is_running:
            self.is_running = True
            self.elapsedTimer.start()

    def pause(self):
        if self.is_running:
            self.time_passed += self.elapsedTimer.elapsed()
            self.is_running = False

    def reset(self):
        self.time_passed = 0
        self.is_running = False

    def elapsedTime(self):
        if self.is_running:
            return (self.time_passed + self.elapsedTimer.elapsed()) / 1000
        return self.time_passed / 1000

def display_graph(start_date=None, end_date=None, show_focus=True, show_goal=True, show_week_average=True):
    data = get_all_database()
    data = sorted(data, key=lambda x: x[0])

    if start_date == None:
        start_date = data[0][0]
    if end_date == None:
        end_date = data[-1][0]
    start_date = date(*[int(i) for i in start_date.split('-')])
    end_date = date(*[int(i) for i in end_date.split('-')])

    if start_date > end_date:
        start_date, end_date = end_date, start_date

    data = {i[0]:[i[1], i[2]] for i in data} # Turn the data into dict

    x_index = []
    x_labels = []
    y_focus = []
    y_goal = []
    y_average = []

    i = -1
    working_day = None
    while working_day != end_date:
        i += 1
        working_day = start_date + timedelta(days=i)

        x_index.append(i)
        x_labels.append(str(working_day))

        if show_focus:
            if str(working_day) in data:
                y_focus.append(data[str(working_day)][0])
            else:
                y_focus.append(0)
        if show_goal:
            if str(working_day) in data:
                y_goal.append(data[str(working_day)][1])
            else:
                y_goal.append(None)
        if show_week_average:
            if len(y_focus) > 6:
                y_average.append(sum(y_focus[-7:])/7)
            else:
                last_7_data = []
                for j in range(0, -7, -1):
                    _w = working_day + timedelta(days=j)
                    if str(_w) in data:
                        last_7_data.append(data[str(_w)][0])
                    else:
                        last_7_data.append(0)
                y_average.append(sum(last_7_data)/7)

    fig, ax = plt.subplots()

    if show_focus:
        ax.plot(x_index, y_focus, label="Focus Time", color="blue")
    if show_goal:
        ax.plot(x_index, y_goal, label="Goal", color="red")
    if show_week_average:
        ax.plot(x_index, y_average, label="Last 7 days average", color="orange")

    ax.set_xticks(x_index)
    ax.set_xticklabels(x_labels)

    ax.set_title("Focus Pad Graph Analysis")
    ax.set_xlabel("Date")
    ax.set_ylabel("Value (Minutes)")

    plt.xticks(rotation=45)
    plt.subplots_adjust(bottom=0.2)

    ax.legend()
    plt.show()

def get_first_last_date():
    data = sorted(get_all_database(), key=lambda x: x[0])
    first, last = data[0][0], data[-1][0]
    return [int(i) for i in first.split('-')], [int(i) for i in last.split('-')]

def is_database_empty():
    cursor = connection.cursor()
    has_rows = cursor.execute("SELECT EXISTS(SELECT 1 FROM days)").fetchone()[0]
    return not has_rows
