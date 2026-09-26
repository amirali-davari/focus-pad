'''
TODO:
 - Add working database
 - Transfer all data from TFT to new database
 - Add date editing and database diting functionality
 - Handle None output from functions.get_info()
 - Add stopwatch functionality
 - Add graph functionality
 - Disable Graph and options to change date when stopwatch is running
 - System tray icon
 - Warning when goal is not reached
'''
from PySide6.QtWidgets import QApplication, QWidget, QMainWindow, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QProgressBar, QFrame, QDialogButtonBox, QComboBox, QSpinBox, QDialog, QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon

import functions
import qtawesome
from jdatetime import date, timedelta

functions.startup()

today = date.today()
selected_date = date.today()

class MainWindow(QMainWindow):
    def __init__(self):
        #Init
        super().__init__()

        self.setWindowTitle('Focus Pad')
        self.setWindowIcon(qtawesome.icon('fa5s.book'))

        self.gtdwindow = None
        self.rawDatabaseWindow = None

        # Menu bar
        menubar = self.menuBar()
        dateMenu = menubar.addMenu('Date')
        todayAction = dateMenu.addAction(qtawesome.icon('fa5s.calendar-day'), 'Go to today')
        todayAction.triggered.connect(lambda: self.set_selected_date(today))
        manualDateAction = dateMenu.addAction(qtawesome.icon('fa5s.calendar-alt'), 'Go to...')
        manualDateAction.triggered.connect(self.manualDateSelect)
        editMenu = menubar.addMenu('Edit')
        editDateAction = editMenu.addAction(qtawesome.icon('mdi.calendar-edit'), 'Edit this date') # Open pop-up and edit data
        editDatabaseAction = editMenu.addAction(qtawesome.icon('mdi.database-edit'), 'View and edit database')
        editDatabaseAction.triggered.connect(self.rawDatabaseEditAction)
        resetDatabaseAction = editMenu.addAction(qtawesome.icon('mdi6.database-sync'), 'Reset database')
        resetDatabaseAction.triggered.connect(self.resetDatabase)
        graphMenu = menubar.addMenu('Graph')
        alltimeGraphAction = graphMenu.addAction(qtawesome.icon('fa5s.database'), 'Full graph') # Display matplotlib full time all data graph
        customGraphAction = graphMenu.addAction(qtawesome.icon('msc.graph-line'), 'Custom graph') # Open pop-up for graph settings and display using matplotlib

        # Main layout
        container = QWidget()
        self.setCentralWidget(container)
        layout = QVBoxLayout(container)

        # Top date text
        date_container = QWidget()
        date_layout = QHBoxLayout(date_container)
        self.date_formatted_label = QLabel(functions.formatted_string_date(selected_date))
        self.date_formatted_label.setAlignment(Qt.AlignCenter)
        self.date_formatted_label.setStyleSheet("font-size: 20px;")

        pr_button = QPushButton()
        pr_button.setIcon(qtawesome.icon("fa5s.chevron-left"))
        pr_button.setMinimumSize(QSize(50, 50))
        pr_button.setMaximumSize(QSize(50, 50))
        pr_button.clicked.connect(lambda: self.set_selected_date(selected_date + timedelta(days=-1)))

        nx_button = QPushButton()
        nx_button.setIcon(qtawesome.icon("fa5s.chevron-right"))
        nx_button.setMinimumSize(QSize(50, 50))
        nx_button.setMaximumSize(QSize(50, 50))
        nx_button.clicked.connect(lambda: self.set_selected_date(selected_date + timedelta(days=1)))

        for w in (pr_button, self.date_formatted_label, nx_button):
            date_layout.addWidget(w)

        # Focus time + Goal
        info_container = QWidget()
        info_layout = QHBoxLayout(info_container)
        sdate_info = functions.get_info(selected_date)
        # WARNING Handle None properly
        if sdate_info == None:
            sdate_info = (0, 1)

        ftime_container = QWidget()
        ftime_layout = QHBoxLayout(ftime_container)
        self.ftime_label = QLabel(f"Focus time: {functions.formatted_string_time(sdate_info[0])}")
        ftime_icon = QLabel()
        ftime_icon.setPixmap(qtawesome.icon('fa5s.brain').pixmap(QSize(20, 20)))
        ftime_icon.setMaximumSize(QSize(20, 20))
        ftime_layout.addWidget(ftime_icon)
        ftime_layout.addWidget(self.ftime_label)

        gtime_container = QWidget()
        gtime_layout = QHBoxLayout(gtime_container)
        self.gtime_label = QLabel(f"Goal: {functions.formatted_string_time(sdate_info[1])}")
        gtime_icon = QLabel()
        gtime_icon.setPixmap(qtawesome.icon('fa5s.clock').pixmap(QSize(20, 20)))
        gtime_icon.setMaximumSize(QSize(20, 20))
        gtime_layout.addWidget(gtime_icon)
        gtime_layout.addWidget(self.gtime_label)

        info_layout.addWidget(ftime_container, alignment=Qt.AlignmentFlag.AlignCenter)
        info_layout.addWidget(gtime_container, alignment=Qt.AlignmentFlag.AlignCenter)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(min(round(100*sdate_info[0]/sdate_info[1]), 100))

        # Remaining info label
        self.re_container = QWidget()
        re_layout = QHBoxLayout(self.re_container)
        re_icon = QLabel()
        re_icon.setPixmap(qtawesome.icon('fa5s.clipboard-check').pixmap(QSize(20, 20)))
        re_icon.setMaximumSize(QSize(20, 20))
        fc_left = sdate_info[1]-sdate_info[0]
        til_midnight = functions.time_left_til_midnight()
        self.remaining_label = QLabel(f'Focus for {functions.formatted_string_time(fc_left)} in the next {functions.formatted_string_time(til_midnight)} to reach the goal of the day. To do so you have to focus for {round(fc_left*60/til_midnight)} minutes per hour.')
        if sdate_info[0] >= sdate_info[1]:
            self.remaining_label.setText('You have reached your goal. Great job!')
        self.remaining_label.setAlignment(Qt.AlignCenter)
        re_layout.addWidget(re_icon, alignment=Qt.AlignmentFlag.AlignRight)
        re_layout.addWidget(self.remaining_label)

        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)

        # Stopwatch
        self.stopwatch_label = QLabel('00:00') # MM:SS --> when MM gets past 60 --> H:MM:SS
        self.stopwatch_label.setAlignment(Qt.AlignCenter)
        self.stopwatch_label.setStyleSheet("font-size: 50px;")
        stopwatch_controls_container = QWidget()
        stopwatch_controls_layout = QHBoxLayout(stopwatch_controls_container)
        start_pause_button = QPushButton('Start focusing') # Change icon to 'fa5s.pause' and change text to Pause focusing when it's running
        start_pause_button.setIcon(qtawesome.icon('fa5s.play'))
        stop_button = QPushButton('Stop focusing')
        stop_button.setIcon(qtawesome.icon('fa5s.stop'))
        stopwatch_controls_layout.addWidget(start_pause_button)
        stopwatch_controls_layout.addWidget(stop_button)
        stopwatch_controls_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)


        self.to_show_only_today = (self.re_container, separator, self.stopwatch_label, stopwatch_controls_container)
        # Add main layout widgets
        layout.addWidget(date_container)
        layout.addWidget(info_container)
        layout.addWidget(self.progress_bar)
        layout.addWidget(self.re_container, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(separator)
        layout.addWidget(self.stopwatch_label)
        layout.addWidget(stopwatch_controls_container)

    def set_selected_date(self, new_date):
        global selected_date
        selected_date = new_date
        sdate_info = functions.get_info(selected_date)
        # WARNING Handle None properly
        if sdate_info == None:
            sdate_info = (0, 1)
        self.date_formatted_label.setText(functions.formatted_string_date(selected_date))
        self.ftime_label.setText(f'Focus time: {functions.formatted_string_time(sdate_info[0])}')
        self.gtime_label.setText(f"Goal: {functions.formatted_string_time(sdate_info[1])}")
        self.progress_bar.setValue(min(round(100*sdate_info[0]/sdate_info[1]), 100))
        if selected_date == today:
            for w in self.to_show_only_today:
                w.show()
        else:
            for w in self.to_show_only_today:
                w.hide()

    def refresh(self):
        self.set_selected_date(selected_date)

    def manualDateSelect(self):
        self.gtdwindow = GoToDateWindow(window)
        self.gtdwindow.show()

    def rawDatabaseEditAction(self):
        self.rawDatabaseWindow = RawDatabaseEditWindow(window)
        self.rawDatabaseWindow.show()

    def resetDatabase(self):
        if QMessageBox.question(self, 'Reset all data?', "Do you really want to delete your current database? This action will lead to data loss! It's recommended to take a backup from your database before proceeding.") == QMessageBox.No:
            return
        if QMessageBox.question(self, 'Really sure?', "This is the last warning! You are about to delete your database! Proceed?") == QMessageBox.No:
            return
        functions.reset_database()
        self.set_selected_date(today)
        QMessageBox.information(self, 'Done!', 'All the data was successfully deleted. Starting fresh!')


class GoToDateWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle('Go to custom date')
        self.setWindowIcon(qtawesome.icon('fa5s.book'))
        self.setFixedSize(350, 150)

        layout = QVBoxLayout(self)

        label = QLabel('Select date to display.')
        label.setAlignment(Qt.AlignCenter)

        input_container = QWidget()
        input_layout = QHBoxLayout(input_container)

        year = QSpinBox()
        year.setRange(1000, 9999)
        year.setValue(today.year)
        month = QComboBox()
        month.addItems([date(1388, month, 24).strftime("%B") for month in range(1, 13)])
        month.setCurrentIndex(today.month - 1)
        mday = QSpinBox()
        mday.setRange(1, functions.get_month_length(today))
        mday.setValue(today.day)
        month.currentIndexChanged.connect(lambda index:mday.setMaximum(functions.get_month_length(date(year=year.value(), month=index+1, day=24)))) # Change mday max to match month
        year.valueChanged.connect(lambda value:mday.setMaximum(functions.get_month_length(date(year=value, month=month.currentIndex()+1, day=24)))) # Change mday max to match year

        input_layout.addWidget(year)
        input_layout.addWidget(month)
        input_layout.addWidget(mday)

        dialog_buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel
        )
        dialog_buttons.accepted.connect(lambda: self.go(year.value(), month.currentIndex()+1, mday.value()))
        dialog_buttons.rejected.connect(self.close)

        layout.addWidget(label)
        layout.addWidget(input_container)
        layout.addWidget(dialog_buttons)

    def go(self, year, month, day):
        window.set_selected_date(date(year, month, day))
        self.close()

class RawDatabaseEditWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle('View and edit database')
        self.setWindowIcon(qtawesome.icon('fa5s.book'))
        self.setMinimumSize(800, 500)

        layout = QVBoxLayout(self)

        label = QLabel('This is an advanced tool to edit the database. Please be careful not to cause unwanted changes to the database.\nKeep the following notes in mind when editing the database\n 1. The first column (Date) is formatted like this: "YYYY-MM-DD" Please avoid writing data into this column in any other format.\n 2. The second and third columns (Focus Time and Goal) must be integers. Inserting any non-integer value will result in errors.\n 3. Focus Time and Goal have minutes as their unit.\n 4. Database rows will be automatically sorted when saving.')
        # label.setAlignment(Qt.AlignCenter)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Date", "Focus Time", "Goal"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.verticalHeader().setVisible(False)

        # Buttons
        button_container = QWidget()
        button_layout = QHBoxLayout(button_container)

        add_button = QPushButton('Add Row')
        add_button.setIcon(qtawesome.icon('fa5s.calendar-plus'))
        add_button.clicked.connect(self.add_row)

        delete_button = QPushButton("Delete Selected Row")
        delete_button.setIcon(qtawesome.icon('fa5s.calendar-minus'))
        delete_button.clicked.connect(self.delete_row)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save |
            QDialogButtonBox.StandardButton.Cancel
        )

        button_layout.addWidget(add_button)
        button_layout.addWidget(delete_button)
        button_layout.addStretch()
        button_layout.addWidget(buttons)

        buttons.accepted.connect(self.save_data)
        buttons.rejected.connect(self.close)

        layout.addWidget(label)
        layout.addWidget(self.table)
        layout.addWidget(button_container)

        # Fill table
        data = functions.get_all_database()
        self.table.setRowCount(len(data))

        for row, item in enumerate(data):
            self.table.setItem(row, 0, QTableWidgetItem(item[0]))
            self.table.setItem(row, 1, QTableWidgetItem(str(item[1])))
            self.table.setItem(row, 2, QTableWidgetItem(str(item[2])))

    def add_row(self):
        row = self.table.rowCount()
        self.table.insertRow(row)

        # Add empty cells
        for column in range(self.table.columnCount()):
            self.table.setItem(row, column, QTableWidgetItem(""))

        self.table.setCurrentCell(row, 0)
        self.table.editItem(self.table.item(row, 0))

    def delete_row(self):
        row = self.table.currentRow()

        if row >= 0:
            self.table.removeRow(row)

    def save_data(self):
        if QMessageBox.question(self, 'Replace Data?', "Do you really want to replace all the data inside the database with the data from this table? This action may lead to data loss!") == QMessageBox.No:
            return

        data = []

        try:
            for row in range(self.table.rowCount()):
                date = self.table.item(row, 0).text()
                focus_time = self.table.item(row, 1).text()
                goal = self.table.item(row, 2).text()

                if date or focus_time or goal:
                    data.append((date, int(focus_time), int(goal)))

            functions.replace_database(sorted(data, key=lambda x: x[0]))

            window.refresh()

            self.close()
        except ValueError:
            QMessageBox.critical(self, 'Invalid Data', "Table includes invalid data. Please double check the table and fix any unwanted values or empty cells.")

app = QApplication()

window = MainWindow()
window.show()

app.exec()
