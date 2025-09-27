import os

from PyQt5.QtCore import Qt, QAbstractTableModel, QModelIndex, QTimer, QSize, QElapsedTimer
from PyQt5.QtGui import QPixmap, QIcon, QFont
from PyQt5.QtWidgets import QFrame, QVBoxLayout, QGridLayout, QPushButton, QWidget, QSlider, QTableWidget, QTableView, \
    QHBoxLayout, QFileDialog, QSplitter, QLabel, QProgressBar, QSizePolicy, QComboBox

import matplotlib

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure

import pandas as pd

import time

from collections import deque

import board

from .themeManager import themeManager

import nums

import autoTest

matplotlib.use('Qt5Agg')
matplotlib.rcParams.update({
    # Figure backgrounds
    "figure.facecolor":   "#1e1e1e",
    "figure.edgecolor":   "#2e2e2e",

    # Axes backgrounds
    "axes.facecolor":     "#2a2a2a",
    "axes.edgecolor":     "#ffffff",

    # Text colors
    "text.color":         "#ffffff",
    "axes.labelcolor":    "#dddddd",
    "axes.titleweight":   "bold",

    # Tick colors
    "xtick.color":        "#bbbbbb",
    "ytick.color":        "#bbbbbb",

    # Grid lines (if you use them)
    "grid.color":         "#444444",
})


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

        graph1 = AutoUpdateGraph(board.cell1Received)
        graph1.setTitle("Thrust")
        graph1.setYAxisTitle("(g)")
        graph2 = AutoUpdateGraph(board.cell2Received)
        graph2.setTitle("Torque")
        graph2.setYAxisTitle("(Nm)")
        graph3 = AutoUpdateGraph(board.voltageReceived)
        graph3.setTitle("Voltage")
        graph3.setYAxisTitle("(V)")
        graph4 = AutoUpdateGraph(board.currentReceived)
        graph4.setTitle("Current")
        graph4.setYAxisTitle("(A)")
        monitorLayout.addWidget(graph1, 0, 0)
        monitorLayout.addWidget(graph2, 0, 1)
        monitorLayout.addWidget(graph3, 1, 0)
        monitorLayout.addWidget(graph4, 1, 1)

        throttleSlider = QSlider(Qt.Horizontal)
        throttleSlider.setMinimum(0)
        throttleSlider.setMaximum(100)
        throttleSlider.setValue(0)
        throttleSlider.valueChanged.connect(board.setThrottle)
        throttleSlider.setTickPosition(QSlider.TicksBelow)
        throttleSlider.setTickInterval(10)
        monitorLayout.addWidget(throttleSlider, 3, 0, 1, 2)

        dataSave = DataSave(graph1.getLastValue, graph2.getLastValue, graph3.getLastValue, graph4.getLastValue, throttleSlider.value)
        splitter.addWidget(dataSave)

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

    def __init__(self, getCell1, getCell2, getCurrent, getVoltage, getThrottle):
        super().__init__()

        self.getCell1 = getCell1
        self.getCell2 = getCell2
        self.getCurrent = getCurrent
        self.getVoltage = getVoltage
        self.getThrottle = getThrottle

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

        exportButton = QPushButton("Export Data")
        exportButton.clicked.connect(self.exportData)
        controlsLayout.addWidget(exportButton)

        clearButton = QPushButton("Clear Data")
        clearButton.clicked.connect(self.clearData)
        controlsLayout.addWidget(clearButton)

        mainLayout.addLayout(controlsLayout)

    def addPoint(self, timer=None):
        dataPoint = {
            "Time": timer if timer is not None and timer != False else self.timerWidget.getTimerValue(),
            "Throttle": self.getThrottle(),
            "Thrust": self.getCell1(),
            "Torque": self.getCell2(),
            "Voltage": self.getVoltage(),
            "Current": self.getCurrent()
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


"""class DataGraph(FigureCanvasQTAgg):
    def __init__(self, history=30):
        fig = Figure(constrained_layout=True)
        self.axes = fig.add_subplot(111)
        self.axes.set_xlim(history, 0)
        self.axes.set_xlabel("time (s)")
        # Add a fixed grey x-axis line at y=0
        self._xaxis_line = self.axes.axhline(0, color="#888", linewidth=1, zorder=1)
        super().__init__(fig)

    def updateGraph(self):
        self.axes.relim()
        self.axes.autoscale(axis='y')
        ymin, ymax = self.axes.get_ylim()
        # Always include y=0 in the visible range
        self.axes.set_ylim(bottom=min(-1, ymin), top=max(1, ymax))
        # Update x-axis line to span current x-limits
        xlim = self.axes.get_xlim()
        self._xaxis_line.set_xdata(xlim)
        self.draw_idle()

    def changeTimeFrame(self, start, end):
        self.axes.set_xlim(end, start)

    def setTitle(self, title):
        self.axes.set_title(title)

    def setXAxisTitle(self, title):
        self.axes.set_xlabel(title)

    def setYAxisTitle(self, title):
        self.axes.set_ylabel(title)


class AutoUpdateGraph(DataGraph):
    """
#    Data transmitted by the signal has to be of a number
"""

    def __init__(self, signal):
        super().__init__()
        self.data = TimedBuffer(180)
        self._plotRef = None
        signal.connect(self.updateData)

    def updateData(self, data):
        self.data.add(data)
        xdata, ydata = zip(*self.data.get_items_by_age(0, 30))
        now = time.time()
        xdata = [now - x for x in xdata]
        if self._plotRef is not None:
            self._plotRef.set_xdata(xdata)
            self._plotRef.set_ydata(ydata)
        else:
            self._plotRef = self.axes.plot(xdata, ydata)[0]

        self.updateGraph()

    def getLastValue(self):
        return self.data.get_values()[-1] if self.data.get_values() else None"""

# chatgpt optimizations, revisit this and clean up code
class DataGraph(FigureCanvasQTAgg):
    def __init__(self, history=30):
        fig = Figure(constrained_layout=True)
        self.axes = fig.add_subplot(111)
        self.axes.set_xlim(history, 0)
        self.axes.set_xlabel("time (s)")
        self._xaxis_line = self.axes.axhline(0, color="#888", linewidth=1, zorder=1)
        super().__init__(fig)

    def updateGraph(self):
        # Only rescale Y when necessary
        self.axes.relim()
        self.axes.autoscale_view(scaley=True)

        ymin, ymax = self.axes.get_ylim()
        self.axes.set_ylim(bottom=min(-1, ymin), top=max(1, ymax))

        # Update x-axis line without recreating it
        self._xaxis_line.set_xdata(self.axes.get_xlim())

        # Much lighter than self.draw()
        self.draw_idle()

    def changeTimeFrame(self, start, end):
        self.axes.set_xlim(end, start)

    def setTitle(self, title):
        self.axes.set_title(title)

    def setXAxisTitle(self, title):
        self.axes.set_xlabel(title)

    def setYAxisTitle(self, title):
        self.axes.set_ylabel(title)


class AutoUpdateGraph(DataGraph):
    def __init__(self, signal, history=30):
        super().__init__(history=history)
        self.data = TimedBuffer(180)
        self._plotRef, = self.axes.plot([], [], lw=1.5)  # Pre-create line for efficiency
        self._history = history
        signal.connect(self.updateData)

    def updateData(self, data):
        self.data.add(data)

        # Get only the most recent data within the window
        items = self.data.get_items_by_age(0, self._history)
        if not items:
            return

        # Unpack just once for efficiency
        timestamps, ydata = zip(*items)
        now = time.time()

        # Convert timestamps into relative x-values in one pass
        xdata = [now - t for t in timestamps]

        # Directly update existing line, don't recreate
        self._plotRef.set_data(xdata, ydata)

        # Avoid unnecessary redraws
        self.updateGraph()

    def getLastValue(self):
        values = self.data.get_values()
        return values[-1] if values else None

