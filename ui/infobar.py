from PyQt5.QtWidgets import QFrame, QHBoxLayout, QLabel, QPushButton, QVBoxLayout


class InfoBar(QFrame):
    def __init__(self):
        super().__init__()

        # set stylesheet
        qss = "resources/infbar.qss"
        with open(qss, "r") as f:
            self.setStyleSheet(f.read())

        self.setFixedHeight(21)

        self.mainLayout = QHBoxLayout(self)
        self.mainLayout.setContentsMargins(0, 0, 0, 0)
        self.mainLayout.setSpacing(0)

        boardStatusLabel = QLabel()
        boardStatusLabel.setText("CONNECTED")
        boardStatusLabel.setObjectName("green")

        self.mainLayout.addWidget(boardStatusLabel)
