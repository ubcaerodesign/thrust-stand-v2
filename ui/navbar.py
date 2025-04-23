from PyQt5.QtWidgets import QFrame, QVBoxLayout, QPushButton


class NavBar(QFrame):
    def __init__(self):
        super().__init__()

        # set stylesheet
        qss = "resources/navbar.qss"
        with open(qss, "r") as f:
            self.setStyleSheet(f.read())

        # spacing and formatting setup
        self.setFixedWidth(200)  # locked width
        sb_layout = QVBoxLayout(self)
        sb_layout.setContentsMargins(10, 10, 10, 10)
        sb_layout.setSpacing(0)

        # add nav buttons (or any widgets)
        self.testBtn = QPushButton("TEST")
        self.connectBtn = QPushButton("CONNECT")
        self.boardBtn = QPushButton("BOARD")
        self.settingsBtn = QPushButton("SETTINGS")
        sb_layout.addWidget(self.testBtn)
        sb_layout.addWidget(self.connectBtn)
        sb_layout.addWidget(self.boardBtn)
        sb_layout.addWidget(self.settingsBtn)

        # pushes all buttons to top
        sb_layout.addStretch()