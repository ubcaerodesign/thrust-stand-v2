from PyQt5.QtWidgets import QFrame, QVBoxLayout, QPushButton


class NavBar(QFrame):
    def __init__(self):
        super().__init__()

        # set stylesheet
        qss = "resources/navbar.qss"
        with open(qss, "r") as f:
            self.setStyleSheet(f.read())

        self.setFixedWidth(200)  # locked width
        sb_layout = QVBoxLayout(self)
        sb_layout.setContentsMargins(10, 10, 10, 10)
        sb_layout.setSpacing(0)

        # add nav buttons (or any widgets)
        for name in ("TEST", "CONNECTION", "SETTINGS"):
            btn = QPushButton(name)
            sb_layout.addWidget(btn)
        sb_layout.addStretch()