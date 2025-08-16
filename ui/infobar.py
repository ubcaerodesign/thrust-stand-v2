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

        self.boardStatusLabel = QLabel()
        self.setDisconnected()

        self.mainLayout.addWidget(self.boardStatusLabel)

    def setConnected(self):
        self.boardStatusLabel.setText("CONNECTED")
        self.boardStatusLabel.setObjectName("green")
        self.boardStatusLabel.style().unpolish(self.boardStatusLabel)
        self.boardStatusLabel.style().polish(self.boardStatusLabel)
        self.boardStatusLabel.update()

    def setDisconnected(self):
        self.boardStatusLabel.setText("NOT CONNECTED")
        self.boardStatusLabel.setObjectName("red")
        self.boardStatusLabel.style().unpolish(self.boardStatusLabel)
        self.boardStatusLabel.style().polish(self.boardStatusLabel)
        self.boardStatusLabel.update()
