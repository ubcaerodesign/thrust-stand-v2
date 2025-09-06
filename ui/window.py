from PyQt5.QtWidgets import QMainWindow, QHBoxLayout, QWidget, QVBoxLayout

from .navbar import NavBar
from .infobar import InfoBar
from .connect import Connect
from .settings import Settings
from .test import Test
from .board import Board

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AeroThrust")
        self.setMinimumSize(1100, 600)
        self.resize(1100, 600)

        infBar = InfoBar()

        self.activeWindows = {
            "Connect": [True, Connect(infBar.setConnected, infBar.setDisconnected)],
            "Test": [False, Test()],
            "Board": [False, Board()],
            "Settings": [False, Settings()]
        }

        self.mainLayout = QVBoxLayout()
        self.mainLayout.setContentsMargins(0, 0, 0, 0)
        self.mainLayout.setSpacing(0)

        self.horLayout = QHBoxLayout()
        self.horLayout.setContentsMargins(0, 0, 0, 0)
        self.horLayout.setSpacing(0)
        self.mainLayout.addLayout(self.horLayout)

        sidebar = NavBar()
        sidebar.testBtn.clicked.connect(self.test)
        sidebar.connectBtn.clicked.connect(self.connect)
        sidebar.boardBtn.clicked.connect(self.board)
        sidebar.settingsBtn.clicked.connect(self.settings)
        self.horLayout.addWidget(sidebar)

        self.mainLayout.addWidget(infBar)

        self.horLayout.addWidget(self.activeWindows["Connect"][1])
        self.horLayout.addWidget(self.activeWindows["Test"][1])
        self.horLayout.addWidget(self.activeWindows["Board"][1])
        self.horLayout.addWidget(self.activeWindows["Settings"][1])
        self.activeWindows["Test"][1].hide()
        self.activeWindows["Board"][1].hide()
        self.activeWindows["Settings"][1].hide()

        mainWidget = QWidget()
        mainWidget.setLayout(self.mainLayout)
        self.setCentralWidget(mainWidget)

    def test(self):
        self.switchWindow("Test")

    def connect(self):
        self.switchWindow("Connect")

    def board(self):
        self.switchWindow("Board")

    def settings(self):
        self.switchWindow("Settings")

    def switchWindow(self, window):
        for w in self.activeWindows:
            if w == window and not self.activeWindows[w][0]:
                self.activeWindows[w][1].show()
                self.activeWindows[w][0] = True
            elif w != window and self.activeWindows[w][0]:
                self.activeWindows[w][1].hide()
                self.activeWindows[w][0] = False
