from PyQt5.QtWidgets import QFrame, QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QLabel


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
        calibrationPanelLayout = QHBoxLayout()
        calibrationPanel.setLayout(calibrationPanelLayout)

        # label
        lbl = QLabel("Calibration:")
        calibrationPanelLayout.addWidget(lbl, stretch=0)

        # master calibration button
        allCalBtn = QPushButton("All")
        allCalBtn.setStyleSheet("QPushButton {background-color: #48655a}")
        calibrationPanelLayout.addWidget(allCalBtn, stretch=1)

        # individual calibration buttons
        thrustCalBtn = QPushButton("Thrust")
        torqueCalBtn = QPushButton("Torque")
        currentCalBtn = QPushButton("Current")
        voltageCalBtn = QPushButton("Voltage")
        calibrationPanelLayout.addWidget(thrustCalBtn, stretch=1)
        calibrationPanelLayout.addWidget(torqueCalBtn, stretch=1)
        calibrationPanelLayout.addWidget(currentCalBtn, stretch=1)
        calibrationPanelLayout.addWidget(voltageCalBtn, stretch=1)

        mainLayout.addStretch()


class BoardInfo(QWidget):
    def __init__(self):
        super().__init__()
