from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import QFrame, QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QLabel, QGridLayout, QPlainTextEdit, \
    QLayout, QSizePolicy

import board


class Board(QFrame):
    def __init__(self):
        super().__init__()

        # set stylesheet
        qss = "resources/dark.qss"
        with open(qss, "r") as f:
            self.setStyleSheet(f.read())

        # split window into calibration part and board status part
        mainLayout = QHBoxLayout(self)

        calibrationWidget = CalibrationWidget()
        mainLayout.addWidget(calibrationWidget)


class CalibrationWidget(QWidget):
    def __init__(self):
        super().__init__()

        mainLayout = QVBoxLayout(self)
        calibrationPanel = QFrame()
        calibrationPanel.setObjectName("panel")
        mainLayout.addWidget(calibrationPanel)
        calibrationPanelLayout = QGridLayout()
        calibrationPanel.setLayout(calibrationPanelLayout)
        calibrationPanel.setMaximumWidth(1200)

        # label
        lbl = QLabel("Calibration:")
        calibrationPanelLayout.addWidget(lbl, 0, 0, 2, 1)
        lbl.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        # master calibration button
        allCalBtn = QPushButton("All")
        # TODO: create an actual stylesheet
        allCalBtn.setObjectName("greenBtn")
        allCalBtn.setMinimumSize(75, 60)
        allCalBtn.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        allCalBtn.clicked.connect(self.calibrateAll)
        calibrationPanelLayout.addWidget(allCalBtn, 0, 1, 2, 1)

        # individual calibration buttons
        thrustCalBtn = QPushButton("Thrust")
        thrustCalBtn.clicked.connect(board.zeroCell1)
        torqueCalBtn = QPushButton("Torque")
        torqueCalBtn.clicked.connect(board.zeroCell2)
        currentCalBtn = QPushButton("Current")
        currentCalBtn.clicked.connect(board.zeroCurrent)
        voltageCalBtn = QPushButton("Voltage")
        voltageCalBtn.clicked.connect(board.zeroVoltage)
        calibrationPanelLayout.addWidget(thrustCalBtn, 0, 2)
        calibrationPanelLayout.addWidget(torqueCalBtn, 0, 3)
        calibrationPanelLayout.addWidget(currentCalBtn, 0, 4)
        calibrationPanelLayout.addWidget(voltageCalBtn, 0, 5)

        # show up-to-date readings
        self.thrustReading = QPlainTextEdit()
        self.thrustReading.setReadOnly(True)
        self.thrustReading.setFixedHeight(27)
        self.thrustReading.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Minimum)
        board.cell1Received.connect(self.updateThrust)
        self.torqueReading = QPlainTextEdit()
        self.torqueReading.setReadOnly(True)
        self.torqueReading.setFixedHeight(27)
        self.torqueReading.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Minimum)
        board.cell2Received.connect(self.updateTorque)
        self.currentReading = QPlainTextEdit()
        self.currentReading.setReadOnly(True)
        self.currentReading.setFixedHeight(27)
        self.currentReading.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Minimum)
        board.currentReceived.connect(self.updateCurrent)
        self.voltageReading = QPlainTextEdit()
        self.voltageReading.setReadOnly(True)
        self.voltageReading.setFixedHeight(27)
        self.voltageReading.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Minimum)
        board.voltageReceived.connect(self.updateVoltage)
        calibrationPanelLayout.addWidget(self.thrustReading, 1, 2)
        calibrationPanelLayout.addWidget(self.torqueReading, 1, 3)
        calibrationPanelLayout.addWidget(self.currentReading, 1, 4)
        calibrationPanelLayout.addWidget(self.voltageReading, 1, 5)

        mainLayout.addStretch()

    def calibrateAll(self):
        board.zeroCell1()
        board.zeroCell2()
        board.zeroCurrent()
        board.zeroVoltage()

    def updateThrust(self, data: int):
        self.thrustReading.setPlainText(str(data) + "g")

    def updateTorque(self, data: int):
        self.torqueReading.setPlainText(str(data) + "g")

    def updateCurrent(self, data: float):
        self.currentReading.setPlainText(str(data) + "A")

    def updateVoltage(self, data: float):
        self.voltageReading.setPlainText(str(data) + "V")


class BoardInfo(QWidget):
    def __init__(self):
        super().__init__()
