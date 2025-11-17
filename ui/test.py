import os

import numpy as np
from PyQt5.QtCore import Qt, QAbstractTableModel, QModelIndex, QTimer, QSize, QElapsedTimer, pyqtSlot
from PyQt5.QtGui import QPixmap, QIcon, QFont
from PyQt5.QtWidgets import QFrame, QVBoxLayout, QGridLayout, QPushButton, QWidget, QSlider, QTableWidget, QTableView, \
    QHBoxLayout, QFileDialog, QSplitter, QLabel, QProgressBar, QSizePolicy, QComboBox

import pyqtgraph as pg

import pandas as pd

import time

from collections import deque

import board

from .themeManager import themeManager

import nums

import autoTest


class Test(QFrame):
    def __init__(self):
        super().__init__()

        # setup stylesheet
        self.setStyleSheet(themeManager.getThemeStylesheet())
        themeManager.themeChanged.connect(self.setTheme)

        mainLayout = QVBoxLayout(self)
        splitter = QSplitter(Qt.Horizontal)
        mainLayout.addWidget(splitter)

        monitorLayout = QGridLayout()
        monitorWidget = QWidget()
        monitorWidget.setLayout(monitorLayout)
        monitorWidget.setMinimumSize(500, 0)
        splitter.addWidget(monitorWidget)

        graph1 = AutoUpdateGraph()
        graph1.setYAxisTitle("Thrust (g)")
        graph1.setXAxisTitle("Samples")
        board.cell1Received.connect(graph1.addPointInt)
        graph2 = AutoUpdateGraph()
        graph2.setYAxisTitle("Torque (Nm)")
        graph2.setXAxisTitle("Samples")
        board.cell2Received.connect(graph2.addPointInt)
        graph3 = AutoUpdateGraph()
        graph3.setYAxisTitle("Voltage (V)")
        graph3.setXAxisTitle("Samples")
        board.voltageReceived.connect(graph3.addPointFloat)
        graph4 = AutoUpdateGraph()
        graph4.setYAxisTitle("Current (A)")
        graph4.setXAxisTitle("Samples")
        board.currentReceived.connect(graph4.addPointFloat)
        monitorLayout.addWidget(graph1, 0, 0)
        monitorLayout.addWidget(graph2, 0, 1)
        monitorLayout.addWidget(graph3, 1, 0)
        monitorLayout.addWidget(graph4, 1, 1)

        throttleSlider = QSlider(Qt.Horizontal)
        throttleSlider.setMinimum(0)
        throttleSlider.setMaximum(100)
        throttleSlider.setValue(0)
        throttleSlider.setTickPosition(QSlider.TicksBelow)
        throttleSlider.setTickInterval(10)
        throttleSlider.valueChanged.connect(board.setThrottle)
        throttleSlider.valueChanged.connect(self.updateThrottleValue)
        monitorLayout.addWidget(throttleSlider, 3, 0, 1, 2)

        self.currentStateData = {
            "Throttle": 0
        }
        dataSave = DataSave(self.currentStateData)
        splitter.addWidget(dataSave)

    def updateThrottleValue(self, value):
        self.currentStateData["Throttle"] = value

    def setTheme(self, stylesheet):
        self.setStyleSheet(stylesheet)


class DataSave(QWidget):
    class PandasTable(QAbstractTableModel):
        """
        Table class that displays the pd dataframe
        """
        def __init__(self, df=pd.DataFrame(), parent=None):
            super().__init__(parent)
            self.df = df

        def rowCount(self, parent=None):
            return len(self.df.index)

        def columnCount(self, parent=None):
            return len(self.df.columns)

        def data(self, index, role=Qt.DisplayRole):
            if index.isValid() and role == Qt.DisplayRole:
                return str(self.df.iat[index.row(), index.column()])
            return None

        def headerData(self, section, orientation, role=Qt.DisplayRole):
            if role == Qt.DisplayRole:
                if orientation == Qt.Horizontal:
                    return str(self.df.columns[section])
                if orientation == Qt.Vertical:
                    return str(self.df.index[section])
            return None

        def appendRow(self, row_dict):
            new_index = len(self.df)
            self.beginInsertRows(QModelIndex(), new_index, new_index)
            self.df.loc[new_index] = row_dict
            self.endInsertRows()

    class TimerWidget(QWidget):
        def __init__(self):
            super().__init__()

            iconBtnQss = "resources/iconBtn.qss"
            iconBtnStyle = None
            with open(iconBtnQss, "r") as f:
                iconBtnStyle = f.read()

            mainLayout = QHBoxLayout(self)

            self.timer = QElapsedTimer()
            self.timer.restart()

            self.timeDelta = 0
            self.timePausedTimestamp = 0
            self.timerPaused = True

            self.uiUpdateTimer = QTimer()
            self.uiUpdateTimer.timeout.connect(self.updateUI)
            self.uiUpdateTimer.start(100)

            timerPixmap = QPixmap("icons/timer.png")
            timerIconLabel = QLabel()
            timerIconLabel.setPixmap(timerPixmap)
            timerIconLabel.setScaledContents(True)
            timerIconLabel.setFixedSize(30, 32)
            mainLayout.addWidget(timerIconLabel)

            self.timerLabel = QLabel()
            self.timerLabel.setText('<span style="color:#555555;">000.0</span>')
            self.timerLabel.setObjectName("large")
            self.timerLabel.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
            self.timerLabel.setAlignment(Qt.AlignCenter)
            mainLayout.addWidget(self.timerLabel)

            self.pauseAndResumeBtn = QPushButton()
            connectIcon = QIcon("icons/play.png")
            self.pauseAndResumeBtn.setIcon(connectIcon)
            self.pauseAndResumeBtn.setIconSize(QSize(20, 20))
            self.pauseAndResumeBtn.setStyleSheet(iconBtnStyle)
            self.pauseAndResumeBtn.clicked.connect(self.pauseAndResume)
            mainLayout.addWidget(self.pauseAndResumeBtn)

            resetBtn = QPushButton()
            refreshIcon = QIcon("icons/refresh.png")
            resetBtn.setIcon(refreshIcon)
            resetBtn.setIconSize(QSize(18, 18))
            resetBtn.setStyleSheet(iconBtnStyle)
            resetBtn.clicked.connect(self.resetTimer)
            mainLayout.addWidget(resetBtn)

        def updateUI(self):
            if not self.timerPaused:
                self.updateTimerLabel(self.timer.elapsed() - self.timeDelta)

        def pauseAndResume(self):
            if self.timerPaused:
                self.beginTimer()
                self.pauseAndResumeBtn.setIcon(QIcon("icons/pause.png"))
            else:
                self.pauseTimer()
                self.pauseAndResumeBtn.setIcon(QIcon("icons/play.png"))

        def beginTimer(self):
            self.timeDelta = self.timer.elapsed() - self.timePausedTimestamp
            self.timerPaused = False

        def pauseTimer(self):
            self.timePausedTimestamp = self.timer.elapsed() - self.timeDelta
            self.timerPaused = True

        def resetTimer(self):
            if not self.timerPaused:
                self.pauseAndResume()
            self.timer.restart()
            self.timeDelta = 0
            self.timePausedTimestamp = 0
            self.updateTimerLabel(self.timer.elapsed() - self.timeDelta)

        def updateTimerLabel(self, value):
            """
            Vibecoded, I will probably have a j*b if I can write code this clean
            Cool piece of code that updates the timer display while making leading 0s gray

            Update self.timeLabel with a formatted time display.

            Parameters:
            - value: time in milliseconds (int)

            Display format: 000.0
            - Leading zeros in gray (#808080)
            - Significant digits in white (#FFFFFF)
            """
            # Convert milliseconds to seconds with 1 decimal place
            seconds = value / 1000
            time_str = f"{seconds:05.1f}"  # 6 characters total, 1 decimal

            # Separate leading zeros from significant digits
            # Leading zeros are all zeros before the first non-zero character (ignoring the decimal point)
            non_zero_index = next((i for i, c in enumerate(time_str.replace('.', '')) if c != '0'), len(time_str))

            # Build HTML string
            html_text = ""
            for i, char in enumerate(time_str):
                if i < non_zero_index:
                    color = "#808080"  # gray for leading zeros
                else:
                    color = "#FFFFFF"  # white for significant digits
                html_text += f'<span style="color:{color};">{char}</span>'

            # Update the label
            self.timerLabel.setText(html_text)

        def getTimerValue(self):
            if self.timerPaused:
                returnValue = self.timePausedTimestamp
            else:
                returnValue = self.timer.elapsed() - self.timeDelta
            if returnValue == 0:
                return None
            return returnValue

    class AutoTestWidget(QWidget):
        def __init__(self, addPoint):
            super().__init__()

            self.addPoint = addPoint

            mainLayout = QHBoxLayout(self)

            self.scriptSelector = QComboBox()
            scriptEntries = os.listdir("scripts")
            scripts = []
            for entry in scriptEntries:
                fullPath = os.path.join("scripts", entry)
                if os.path.isfile(fullPath):
                    scripts.append(entry)
            self.scriptSelector.addItems(scripts)
            mainLayout.addWidget(self.scriptSelector)

            self.scriptBtn = QPushButton("Start")
            self.scriptBtn.clicked.connect(self.startStopScript)
            self.scriptBtn.setMaximumWidth(60)
            mainLayout.addWidget(self.scriptBtn)

        def startStopScript(self):
            if autoTest.scriptRunning:
                self.cancelScript()
            else:
                self.startScript()

        @staticmethod
        def cancelScript():
            autoTest.cancelScript()

        def startScript(self):
            autoTest.runScript(os.path.join("scripts", self.scriptSelector.currentText()), self.addPoint, self.scriptComplete)
            self.scriptBtn.setText("Cancel")
            self.scriptSelector.setEnabled(False)

        def scriptComplete(self):
            self.scriptBtn.setText("Start")
            self.scriptSelector.setEnabled(True)

    def __init__(self, dataDict):
        super().__init__()

        self.dataDict = dataDict

        self.datasheet = nums.Datasheet(["Time", "Throttle", "Thrust", "Torque", "Voltage", "Current"])

        mainLayout = QVBoxLayout(self)

        self.timerWidget = self.TimerWidget()
        mainLayout.addWidget(self.timerWidget)

        autoTestWidget = self.AutoTestWidget(self.addPoint)
        mainLayout.addWidget(autoTestWidget)

        self.model = self.PandasTable(self.datasheet.getDF())
        self.table = QTableView()
        self.table.setModel(self.model)
        self.table.setMinimumWidth(300)
        self.table.verticalHeader().setVisible(True)
        self.table.verticalHeader().setMinimumWidth(32)
        mainLayout.addWidget(self.table)

        controlsLayout = QHBoxLayout()

        addDataButton = QPushButton("Save Point")
        addDataButton.clicked.connect(self.addPoint)
        controlsLayout.addWidget(addDataButton)

        self.recordDataButton = QPushButton("Record Data")
        self.recordDataButton.clicked.connect(self.recordData)
        self.recording = False
        controlsLayout.addWidget(self.recordDataButton)
        self.recordTimer = QTimer()
        self.recordTimer.timeout.connect(self.addPoint)

        exportButton = QPushButton("Export Data")
        exportButton.clicked.connect(self.exportData)
        controlsLayout.addWidget(exportButton)

        clearButton = QPushButton("Clear Data")
        clearButton.clicked.connect(self.clearData)
        controlsLayout.addWidget(clearButton)

        mainLayout.addLayout(controlsLayout)

    def recordData(self):
        if self.recording:
            self.recording = False
            self.recordDataButton.setText("Record Data")
            self.recordTimer.stop()
        else:
            self.recording = True
            self.recordDataButton.setText("Stop Recording")
            self.recordTimer.start(250)

    def addPoint(self, timer=None, throttle=None):
        dataPoint = {
            "Time": timer if timer is not None and timer != False else self.timerWidget.getTimerValue(),
            "Throttle": throttle if throttle is not None else self.dataDict["Throttle"],
            "Thrust": board.cell1,
            "Torque": board.cell2,
            "Voltage": board.voltage,
            "Current": board.current
        }
        self.datasheet.addPoint(dataPoint)
        self.model.appendRow(dataPoint)

    def exportData(self):
        filePath, _ = QFileDialog.getSaveFileName(
            self,
            "Export Data",
            "",
            "CSV (*.csv);;All Files (*)"
        )
        if filePath:
            self.datasheet.export(filePath)

    def clearData(self):
        self.datasheet = nums.Datasheet(["Time", "Throttle", "Thrust", "Torque", "Voltage", "Current"])
        self.model = self.PandasTable(self.datasheet.getDF())
        self.table.setModel(self.model)


class TimedBuffer:
    """
    Vibecoded, a class that timestamps incoming data and deletes anything too old
    """
    def __init__(self, max_age_secs: float):
        """
        max_age_secs: entries older than this (in seconds) will be discarded
        """
        self.max_age = max_age_secs
        # store pairs (timestamp, value)
        self._buffer = deque()

    def add(self, value):
        """Append a new sample with the current time, then prune old ones."""
        now = time.time()
        self._buffer.append((now, value))
        self._prune(now)

    def _prune(self, now=None):
        """Remove entries older than max_age from the left."""
        if now is None:
            now = time.time()
        cutoff = now - self.max_age
        # keep popping until the oldest one is recent enough
        while self._buffer and self._buffer[0][0] < cutoff:
            self._buffer.popleft()

    def get_times(self):
        """Return list of timestamps currently in the buffer."""
        return [t for t, _ in self._buffer]

    def get_values(self):
        """Return list of values currently in the buffer."""
        return [v for _, v in self._buffer]

    def get_items(self):
        """Return list of (timestamp, value) pairs."""
        return list(self._buffer)

    def clear(self):
        """Empty the buffer completely."""
        self._buffer.clear()

    def get_items_by_age(self, older_than: float, younger_than: float):
        """
        Return list of (timestamp, value) pairs whose age is:
            older than `older_than` seconds (i.e. age > older_than)
        and younger than `younger_than` seconds (i.e. age < younger_than).
        """
        now = time.time()
        results = []
        for ts, val in self._buffer:
            age = now - ts
            if older_than < age < younger_than:
                results.append((ts, val))
        return results


class SignalTimedBuffer(TimedBuffer):
    def __init__(self, max_age_secs: float, signal):
        super().__init__(max_age_secs)
        signal.connect(self.newData)

    def newData(self, data):
        self.add(data)


class AutoUpdateGraph(QWidget):
    """
    Uses a circular buffer to keep track of the incoming data
    """
    def __init__(self, buffer_size=200):
        super().__init__()

        # plotting buffer
        self.buffer_size = buffer_size
        self.data = np.zeros(self.buffer_size)
        self.ptr = 0

        # setup layout + plot
        layout = QVBoxLayout(self)
        self.plot_widget = pg.PlotWidget()
        layout.addWidget(self.plot_widget)
        self.curve = self.plot_widget.plot(self.data)

        # styling
        self.plot_widget.showGrid(x=True, y=True)
        self.plot_widget.setLabel('left', 'y')
        self.plot_widget.setLabel('bottom', 'x')
        self.plot_widget.setBackground('#1e1e1e')

    @pyqtSlot(int)
    def addPointInt(self, value):
        self.data[self.ptr] = value
        self.ptr = (self.ptr + 1) % self.buffer_size
        self.curve.setData(np.roll(self.data, -self.ptr))

    @pyqtSlot(float)
    def addPointFloat(self, value):
        self.data[self.ptr] = value
        self.ptr = (self.ptr + 1) % self.buffer_size
        self.curve.setData(np.roll(self.data, -self.ptr))

    def setTitle(self, title):
        self.plot_widget.setTitle(title)

    def setYAxisTitle(self, title):
        self.plot_widget.setLabel('left', title)
        self.plot_widget.getAxis('left').enableAutoSIPrefix(False)

    def setXAxisTitle(self, title):
        self.plot_widget.setLabel('bottom', title)
        self.plot_widget.getAxis('left').enableAutoSIPrefix(False)
