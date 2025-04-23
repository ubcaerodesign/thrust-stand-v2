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
        calibrationPanelLayout.addWidget(lbl)

        # master calibration button
        allCalBtn = QPushButton("All")
        calibrationPanelLayout.addWidget(allCalBtn)

        # individual calibration buttons
        thrustCalBtn = QPushButton("Thrust")
        torqueCalBtn = QPushButton("Torque")
        currentCalBtn = QPushButton("Current")
        voltageCalBtn = QPushButton("Voltage")
        calibrationPanelLayout.addWidget(thrustCalBtn)
        calibrationPanelLayout.addWidget(torqueCalBtn)
        calibrationPanelLayout.addWidget(currentCalBtn)
        calibrationPanelLayout.addWidget(voltageCalBtn)

        mainLayout.addStretch()


class BoardInfo(QWidget):
    def __init__(self):
        super().__init__()
