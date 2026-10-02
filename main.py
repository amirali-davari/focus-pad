'''
TODO:
 - Make it possible to edit focus time without having to define goal
 - Add graph functionality
 - System tray icon
 - Warning when goal is not reached
 - Add georgian date system
'''
from PySide6.QtWidgets import QApplication, QWidget, QMainWindow, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QProgressBar, QFrame, QDialogButtonBox, QComboBox, QSpinBox, QDialog, QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox, QFileDialog, QCheckBox
from PySide6.QtCore import Qt, QSize, QTimer
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

        self.updateTimer = QTimer()
        self.updateTimer.setInterval(250)
        self.updateTimer.timeout.connect(self.updateLoop)
        self.updateTimer.start()

        self.focusStopwatch = functions.StopwatchLogic()
        self.lastMinuteSaved = 0

        self.gtdwindow = None
        self.rawDatabaseWindow = None
        self.customGraphWindow = None

        # Menu bar
        menubar = self.menuBar()

        dateMenu = menubar.addMenu('Date')
        todayAction = dateMenu.addAction(qtawesome.icon('fa5s.calendar-day'), 'Go to today')
        todayAction.triggered.connect(lambda: self.set_selected_date(today))
        manualDateAction = dateMenu.addAction(qtawesome.icon('fa5s.calendar-alt'), 'Go to...')
        manualDateAction.triggered.connect(self.manualDateSelect)

        editMenu = menubar.addMenu('Edit')
        editDateAction = editMenu.addAction(qtawesome.icon('mdi.calendar-edit'), 'Edit this date')
        editDateAction.triggered.connect(self.editDate)
        editDatabaseAction = editMenu.addAction(qtawesome.icon('mdi.database-edit'), 'View and edit database')
        editDatabaseAction.triggered.connect(self.rawDatabaseEditAction)
        importCSVAction = editMenu.addAction(qtawesome.icon('fa5s.file-import'), 'Import data from CSV file')
        importCSVAction.triggered.connect(self.importCSV)
        resetDatabaseAction = editMenu.addAction(qtawesome.icon('mdi6.database-sync'), 'Reset database')
        resetDatabaseAction.triggered.connect(self.resetDatabase)

        graphMenu = menubar.addMenu('Graph')
        alltimeGraphAction = graphMenu.addAction(qtawesome.icon('fa5s.database'), 'Full graph')
        alltimeGraphAction.triggered.connect(self.fullGraph)
        customGraphAction = graphMenu.addAction(qtawesome.icon('msc.graph-line'), 'Custom graph')
        customGraphAction.triggered.connect(self.customGraph)

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

        self.pr_button = QPushButton()
        self.pr_button.setIcon(qtawesome.icon("fa5s.chevron-left"))
        self.pr_button.setMinimumSize(QSize(50, 50))
        self.pr_button.setMaximumSize(QSize(50, 50))
        self.pr_button.clicked.connect(lambda: self.set_selected_date(selected_date + timedelta(days=-1)))

        self.nx_button = QPushButton()
        self.nx_button.setIcon(qtawesome.icon("fa5s.chevron-right"))
        self.nx_button.setMinimumSize(QSize(50, 50))
        self.nx_button.setMaximumSize(QSize(50, 50))
        self.nx_button.clicked.connect(lambda: self.set_selected_date(selected_date + timedelta(days=1)))

        for w in (self.pr_button, self.date_formatted_label, self.nx_button):
            date_layout.addWidget(w)

        # Focus time + Goal
        info_container = QWidget()
        info_layout = QHBoxLayout(info_container)
        self.sdate_info = functions.get_info(selected_date)
        if self.sdate_info == None:
            self.sdate_info = (0, None)

        ftime_container = QWidget()
        ftime_layout = QHBoxLayout(ftime_container)
        self.ftime_label = QLabel(f"Focus time: {functions.formatted_string_time(self.sdate_info[0])}")
        ftime_icon = QLabel()
        ftime_icon.setPixmap(qtawesome.icon('fa5s.brain').pixmap(QSize(20, 20)))
        ftime_icon.setMaximumSize(QSize(20, 20))
        ftime_layout.addWidget(ftime_icon)
        ftime_layout.addWidget(self.ftime_label)

        gtime_container = QWidget()
        gtime_layout = QHBoxLayout(gtime_container)
        self.gtime_label = QLabel(f"Goal: {functions.formatted_string_time(self.sdate_info[1]) if self.sdate_info[1] != None else 'Undefined'}")
        gtime_icon = QLabel()
        gtime_icon.setPixmap(qtawesome.icon('fa5s.clock').pixmap(QSize(20, 20)))
        gtime_icon.setMaximumSize(QSize(20, 20))
        gtime_layout.addWidget(gtime_icon)
        gtime_layout.addWidget(self.gtime_label)

        info_layout.addWidget(ftime_container, alignment=Qt.AlignmentFlag.AlignCenter)
        info_layout.addWidget(gtime_container, alignment=Qt.AlignmentFlag.AlignCenter)

        # Progress bar
        self.progress_bar = QProgressBar()
        if self.sdate_info[1] == None:
            self.progress_bar.setValue(0)
        elif self.sdate_info[1] == 0:
            self.progress_bar.setValue(100)
        else:
            self.progress_bar.setValue(min(round(100*self.sdate_info[0]/self.sdate_info[1]), 100))

        # Remaining info label
        self.re_container = QWidget()
        re_layout = QHBoxLayout(self.re_container)
        re_icon = QLabel()
        re_icon.setPixmap(qtawesome.icon('fa5s.clipboard-check').pixmap(QSize(20, 20)))
        re_icon.setMaximumSize(QSize(20, 20))
        self.remaining_label = QLabel()
        if self.sdate_info[1] == None:
            self.remaining_label.setText("""Today's goal is not defined yet. Try setting a goal using "Edit this date" action in the menu bar.""")
        elif self.sdate_info[0] >= self.sdate_info[1]:
            self.remaining_label.setText('You have reached your goal. Great job!')
        else:
            til_midnight = functions.time_left_til_midnight()
            fc_left = self.sdate_info[1]-self.sdate_info[0]
            self.remaining_label.setText(f'Focus for {functions.formatted_string_time(fc_left)} in the next {functions.formatted_string_time(til_midnight)} to reach the goal of the day. To do so you have to focus for {round(fc_left*60/til_midnight)} minutes per hour.')
        self.remaining_label.setAlignment(Qt.AlignCenter)
        re_layout.addWidget(re_icon, alignment=Qt.AlignmentFlag.AlignRight)
        re_layout.addWidget(self.remaining_label)

        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)

        # Stopwatch
        self.stopwatch_label = QLabel('00:00')
        self.stopwatch_label.setAlignment(Qt.AlignCenter)
        self.stopwatch_label.setStyleSheet("font-size: 50px;")
        stopwatch_controls_container = QWidget()
        stopwatch_controls_layout = QHBoxLayout(stopwatch_controls_container)
        self.start_pause_button = QPushButton('Start focusing')
        self.start_pause_button.setIcon(qtawesome.icon('fa5s.play'))
        self.start_pause_button.clicked.connect(self.sw_startORpause)
        stop_button = QPushButton('Stop focusing')
        stop_button.setIcon(qtawesome.icon('fa5s.stop'))
        stop_button.clicked.connect(self.sw_stop)
        stopwatch_controls_layout.addWidget(self.start_pause_button)
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
        self.sdate_info = functions.get_info(selected_date)
        if self.sdate_info == None:
            self.sdate_info = (0, None)
        self.date_formatted_label.setText(functions.formatted_string_date(selected_date))
        self.ftime_label.setText(f'Focus time: {functions.formatted_string_time(self.sdate_info[0])}')
        self.gtime_label.setText(f"Goal: {functions.formatted_string_time(self.sdate_info[1]) if self.sdate_info[1] != None else 'Undefined'}")

        if self.sdate_info[1] == None:
            self.progress_bar.setValue(0)
        elif self.sdate_info[1] == 0:
            self.progress_bar.setValue(100)
        else:
            self.progress_bar.setValue(min(round(100*self.sdate_info[0]/self.sdate_info[1]), 100))

        if selected_date == today:
            for w in self.to_show_only_today:
                w.show()
        else:
            for w in self.to_show_only_today:
                w.hide()

    def refresh(self):
        self.set_selected_date(selected_date)

    def manualDateSelect(self):
        self.gtdwindow = GoToDateWindow(self)
        self.gtdwindow.setModal(True)
        self.gtdwindow.show()

    def rawDatabaseEditAction(self):
        self.rawDatabaseWindow = RawDatabaseEditWindow(self)
        self.rawDatabaseWindow.setModal(True)
        self.rawDatabaseWindow.show()

    def resetDatabase(self):
        if QMessageBox.question(self, 'Reset all data?', "Do you really want to delete your current database? This action will lead to data loss! It's recommended to take a backup from your database before proceeding.") == QMessageBox.No:
            return
        if QMessageBox.question(self, 'Really sure?', "This is the last warning! You are about to delete your database! Proceed?") == QMessageBox.No:
            return
        functions.reset_database()
        self.set_selected_date(today)
        if self.focusStopwatch.is_running:
            self.sw_stop()
        QMessageBox.information(self, 'Done!', 'All the data was successfully deleted. Starting fresh!')

    def editDate(self):
        self.editdatewindow = EditDateWindow(self.sdate_info, parent=window)
        self.editdatewindow.setModal(True)
        self.editdatewindow.show()

    def importCSV(self):
        file_path, _ = QFileDialog.getOpenFileName(self, 'Select correctly fotmated CSV file.', '', 'CSV Files (*.csv)')
        if file_path:
            success, error = functions.importCSV(file_path)
            if success:
                QMessageBox.information(self, 'Done!', 'CSV file was imported to your database successfully.')
            elif error == 'BadHeaderError':
                QMessageBox.critical(self, 'Error!', 'The CSV file contains unknown headers in the first row. The first row of your CSV file should look like this: "date, focus_time, goal"')
            elif error == 'ValueError':
                QMessageBox.critical(self, 'Error!', 'The CSV file contains unexpected values. Please search the CSV file for unwanted values.')

    def updateLoop(self):
        global today
        global selected_date
        if date.today() != today:
            if selected_date == today:
                selected_date = date.today()
            today = date.today()
            self.set_selected_date(selected_date)
            if functions.get_info(today) == None:
                functions.dayEdit(today, 0, functions.get_info(today + timedelta(days=-1))[1])

        if selected_date == today:
            self.ftime_label.setText(f'Focus time: {functions.formatted_string_time(self.sdate_info[0])}')

            if self.sdate_info[1] == None:
                self.progress_bar.setValue(0)
            elif self.sdate_info[1] == 0:
                self.progress_bar.setValue(100)
            else:
                self.progress_bar.setValue(min(round(100*self.sdate_info[0]/self.sdate_info[1]), 100))

            if self.sdate_info[1] == None:
                self.remaining_label.setText("""Today's goal is not defined yet. Try setting a goal using "Edit this date" action in the menu bar.""")
            elif self.sdate_info[0] >= self.sdate_info[1]:
                self.remaining_label.setText('You have reached your goal. Great job!')
            else:
                til_midnight = functions.time_left_til_midnight()
                fc_left = self.sdate_info[1]-self.sdate_info[0]
                self.remaining_label.setText(f'Focus for {functions.formatted_string_time(fc_left)} in the next {functions.formatted_string_time(til_midnight)} to reach the goal of the day. To do so you have to focus for {round(fc_left*60/til_midnight)} minutes per hour.')

            self.stopwatch_label.setText(str()) # MM:SS --> when MM gets past 60 --> H:MM:SS
            time_spent = self.focusStopwatch.elapsedTime()
            m, s = divmod(time_spent, 60)
            s = min(59, round(s))
            h, m = divmod(m, 60)
            h, m = int(h), int(m)
            if h > 0:
                self.stopwatch_label.setText(f'{h}:{m if len(str(m)) > 1 else "0"+str(m)}:{s if len(str(s)) > 1 else "0"+str(s)}')
            else:
                self.stopwatch_label.setText(f'{m if len(str(m)) > 1 else "0"+str(m)}:{s if len(str(s)) > 1 else "0"+str(s)}')

            if h*60 + m > self.lastMinuteSaved:
                functions.dayEdit(selected_date, ((h*60 + m) - self.lastMinuteSaved) + self.sdate_info[0], self.sdate_info[1])
                self.sdate_info = functions.get_info(selected_date)
                self.lastMinuteSaved = h*60 + m


    def sw_startORpause(self):
        if self.sdate_info[1] == None:
            QMessageBox.critical(self, 'Error!', 'You can not change your focus time data while goal is undefined. Try setting a goal first.')
            return
        if self.focusStopwatch.is_running:
            self.focusStopwatch.pause()
            self.start_pause_button.setText('Continue focusing')
            self.start_pause_button.setIcon(qtawesome.icon('fa5s.play'))
        else:
            self.focusStopwatch.start()
            self.start_pause_button.setText('Pause focusing')
            self.start_pause_button.setIcon(qtawesome.icon('fa5s.pause'))

    def sw_stop(self):
        self.focusStopwatch.reset()
        self.start_pause_button.setText('Start focusing')
        self.start_pause_button.setIcon(qtawesome.icon('fa5s.play'))
        self.stopwatch_label.setText('00:00')
        self.lastMinuteSaved = 0

    def fullGraph(self):
        if functions.is_database_empty():
            QMessageBox.warning(self, 'Empty database', 'There is no data to display on the graph!')
        else:
            functions.display_graph()

    def customGraph(self):
        if functions.is_database_empty():
            QMessageBox.warning(self, 'Empty database', 'There is no data to display on the graph!')
        else:
            self.customGraphWindow = CustomGraphConfig(self)
            self.customGraphWindow.setModal(True)
            self.customGraphWindow.show()


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

class EditDateWindow(QDialog):
    def __init__(self, date_data, parent=None):
        super().__init__(parent)
        self.sdate_info = date_data
        if self.sdate_info[1] == None:
            gh, gm = 1, 0
        else:
            gh, gm = divmod(self.sdate_info[1], 60)

        self.setWindowTitle(f'Edit {functions.formatted_string_date(selected_date).split(', ')[1]}')
        self.setWindowIcon(qtawesome.icon('fa5s.book'))

        layer = QVBoxLayout(self)

        chooseItem = QComboBox()
        chooseItem.addItems(['Focus Time', 'Goal'])
        chooseItem.currentTextChanged.connect(self.onItemChanged)

        self.currentInfoLabel = QLabel(f'Current focused time: {functions.formatted_string_time(self.sdate_info[0])}')
        self.currentInfoLabel.setAlignment(Qt.AlignCenter)

        # Goal Widgets
        self.goalContainer = QWidget()
        self.goalContainer.hide()
        goalLayer = QHBoxLayout(self.goalContainer)

        goalFirstLabel = QLabel('New goal: ')
        goalFirstLabel.setAlignment(Qt.AlignCenter)
        gHour = QSpinBox()
        gHour.setRange(0, 23)
        gHour.setValue(gh)
        gdotLabel = QLabel(':')
        gdotLabel.setAlignment(Qt.AlignCenter)
        gdotLabel.setMaximumSize(QSize(10, 10))
        gMinute = QSpinBox()
        gMinute.setRange(0, 59)
        gMinute.setValue(gm)
        gHour.valueChanged.connect(lambda value: gMinute.setMinimum(1) if value == 0 else gMinute.setMinimum(0))

        goalLayer.addWidget(goalFirstLabel)
        goalLayer.addWidget(gHour)
        goalLayer.addWidget(gdotLabel)
        goalLayer.addWidget(gMinute)

        # Focus time widgets
        self.focusContainer = QWidget()
        focusLayer = QHBoxLayout(self.focusContainer)

        asComboBox = QComboBox()
        asComboBox.addItems(['Add', 'Subtract'])
        asSpin = QSpinBox()
        asSpin.setRange(1, 1440 - self.sdate_info[0])
        asSpin.setValue(15)
        asComboBox.currentTextChanged.connect(lambda text: asSpin.setMaximum(1440 - self.sdate_info[0]) if text == 'Add' else asSpin.setMaximum(self.sdate_info[0]))
        focusMinuteLabel = QLabel('minutes')
        self.newFocusLabel = QLabel(f'New focus time will be {functions.formatted_string_time(self.sdate_info[0] + (-1 if asComboBox.currentIndex() else 1)*asSpin.value())}.')
        self.newFocusLabel.setAlignment(Qt.AlignCenter)
        asSpin.valueChanged.connect(lambda value: self.newFocusLabel.setText(f'New focus time will be {functions.formatted_string_time(self.sdate_info[0] + (-1 if asComboBox.currentIndex() else 1)*value)}.'))
        asComboBox.currentIndexChanged.connect(lambda index: self.newFocusLabel.setText(f'New focus time will be {functions.formatted_string_time(self.sdate_info[0] + (-1 if index else 1)*asSpin.value())}.'))

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save |
            QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(lambda : self.save_data(chooseItem.currentText(), asComboBox.currentIndex(), asSpin.value(), gHour.value(), gMinute.value()))
        buttons.rejected.connect(self.close)

        focusLayer.addWidget(asComboBox)
        focusLayer.addWidget(asSpin)
        focusLayer.addWidget(focusMinuteLabel)

        layer.addWidget(chooseItem)
        layer.addWidget(self.currentInfoLabel)
        layer.addWidget(self.goalContainer)
        layer.addWidget(self.focusContainer)
        layer.addWidget(self.newFocusLabel)
        layer.addWidget(buttons)

    def onItemChanged(self, text):
        if text == 'Goal':
            self.currentInfoLabel.setText(f'Current goal: {"Undefined" if self.sdate_info[1] == None else functions.formatted_string_time(self.sdate_info[1])}')
            self.goalContainer.show()
            self.focusContainer.hide()
            self.newFocusLabel.hide()
        else:
            self.currentInfoLabel.setText(f'Current focused time: {functions.formatted_string_time(self.sdate_info[0])}')
            self.goalContainer.hide()
            self.focusContainer.show()
            self.newFocusLabel.show()

    def save_data(self, mode, fmode, fvalue, ghvalue, gmvalue):
        if mode == 'Goal':
            functions.dayEdit(selected_date, self.sdate_info[0], ghvalue*60 + gmvalue)
        else:
            if self.sdate_info[1] == None:
                QMessageBox.critical(self, 'Error!', 'You can not change your focus time data while goal is undefined. Try setting a goal first.')
                return
            functions.dayEdit(selected_date, self.sdate_info[0] + (-1 if fmode else 1)*fvalue, self.sdate_info[1])

        window.refresh()
        self.close()

class StartupGoalDefine(QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('Set goal')
        self.setWindowIcon(qtawesome.icon('fa5s.book'))

        layer = QVBoxLayout(self)

        beginLabel = QLabel("Set today's focus goal to get started!")
        beginLabel.setAlignment(Qt.AlignCenter)

        goalContainer = QWidget()
        goalLayer = QHBoxLayout(goalContainer)

        goalFirstLabel = QLabel("Today's goal: ")
        goalFirstLabel.setAlignment(Qt.AlignCenter)
        gHour = QSpinBox()
        gHour.setValue(1)
        gHour.setRange(0, 23)
        gdotLabel = QLabel(':')
        gdotLabel.setAlignment(Qt.AlignCenter)
        gdotLabel.setMaximumSize(QSize(10, 10))
        gMinute = QSpinBox()
        gMinute.setRange(0, 59)
        gHour.valueChanged.connect(lambda value: gMinute.setMinimum(1) if value == 0 else gMinute.setMinimum(0))

        goalLayer.addWidget(goalFirstLabel)
        goalLayer.addWidget(gHour)
        goalLayer.addWidget(gdotLabel)
        goalLayer.addWidget(gMinute)

        dialog_buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel
        )
        dialog_buttons.accepted.connect(lambda: self.ok(gHour.value()*60+gMinute.value()))
        dialog_buttons.rejected.connect(self.close)

        layer.addWidget(beginLabel)
        layer.addWidget(goalContainer)
        layer.addWidget(dialog_buttons)

    def ok(self, g):
        functions.dayEdit(today, 0, g)
        self.close()

class CustomGraphConfig(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle('Custom Graph Configuration')
        self.setWindowIcon(qtawesome.icon('fa5s.book'))

        layer = QVBoxLayout(self)

        beginLabel = QLabel("Configure your graph using the options below.\nSelect starting date:")
        beginLabel.setAlignment(Qt.AlignCenter)

        start_container = QWidget()
        start_layout = QHBoxLayout(start_container)

        first_date = functions.get_first_date()

        syear = QSpinBox()
        syear.setRange(1000, 9999)
        syear.setValue(first_date[0])
        smonth = QComboBox()
        smonth.addItems([date(1388, month, 24).strftime("%B") for month in range(1, 13)])
        smonth.setCurrentIndex(first_date[1] - 1)
        sday = QSpinBox()
        sday.setRange(1, functions.get_month_length(today))
        sday.setValue(first_date[2])
        smonth.currentIndexChanged.connect(lambda index:sday.setMaximum(functions.get_month_length(date(year=syear.value(), month=index+1, day=24))))
        syear.valueChanged.connect(lambda value:sday.setMaximum(functions.get_month_length(date(year=value, month=smonth.currentIndex()+1, day=24))))

        start_layout.addWidget(syear)
        start_layout.addWidget(smonth)
        start_layout.addWidget(sday)

        endLabel = QLabel("Select last date:")
        endLabel.setAlignment(Qt.AlignCenter)

        end_container = QWidget()
        end_layout = QHBoxLayout(end_container)

        eyear = QSpinBox()
        eyear.setRange(1000, 9999)
        eyear.setValue(today.year)
        emonth = QComboBox()
        emonth.addItems([date(1388, month, 24).strftime("%B") for month in range(1, 13)])
        emonth.setCurrentIndex(today.month - 1)
        eday = QSpinBox()
        eday.setRange(1, functions.get_month_length(today))
        eday.setValue(today.day)
        emonth.currentIndexChanged.connect(lambda index:eday.setMaximum(functions.get_month_length(date(year=eyear.value(), month=index+1, day=24))))
        eyear.valueChanged.connect(lambda value:eday.setMaximum(functions.get_month_length(date(year=value, month=emonth.currentIndex()+1, day=24))))

        end_layout.addWidget(eyear)
        end_layout.addWidget(emonth)
        end_layout.addWidget(eday)

        checkbox_container = QWidget()
        checkbox_layout = QHBoxLayout(checkbox_container)
        focus_checkbox = QCheckBox('Focus Time')
        goal_checkbox = QCheckBox('Goal')
        average_checkbox = QCheckBox('Week average focus time')
        for checkbox in (focus_checkbox, goal_checkbox, average_checkbox):
            checkbox.setChecked(True)
            checkbox_layout.addWidget(checkbox)

        dialog_buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel
        )
        dialog_buttons.accepted.connect(lambda: self.ok(f'{syear.value()}-{smonth.currentIndex() + 1}-{sday.value()}', f'{eyear.value()}-{emonth.currentIndex() + 1}-{eday.value()}', focus_checkbox.isChecked(), goal_checkbox.isChecked(), average_checkbox.isChecked()))
        dialog_buttons.rejected.connect(self.close)

        layer.addWidget(beginLabel)
        layer.addWidget(start_container)
        layer.addWidget(endLabel)
        layer.addWidget(end_container)
        layer.addWidget(checkbox_container)
        layer.addWidget(dialog_buttons)

    def ok(self, *args):
        functions.display_graph(*args)
        self.close()

app = QApplication()

if functions.get_info(today) == None:
    sgd = StartupGoalDefine()
    sgd.exec()

window = MainWindow()
window.show()

app.exec()
functions.connection.close()
