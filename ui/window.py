import sys

import PyQt5
from PyQt5 import QtCore
from PyQt5.QtWidgets import QMainWindow, QApplication, QHBoxLayout, QWidget

from .navbar import NavBar
from .connect import Connect
from .test import Test
from .board import Board

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AeroThrust")
        self.setMinimumSize(800, 500)
        self.resize(800, 500)

        self.activeWindows = {
            "Connect": [True, Connect()],
            "Test": [False, Test()],
            "Board": [False, Board()]
        }

        self.mLayout = QHBoxLayout()
        self.mLayout.setContentsMargins(0, 0, 0, 0)
        self.mLayout.setSpacing(0)

        sidebar = NavBar()
        sidebar.testBtn.clicked.connect(self.test)
        sidebar.connectBtn.clicked.connect(self.connect)
        sidebar.boardBtn.clicked.connect(self.board)
        self.mLayout.addWidget(sidebar)

        self.mLayout.addWidget(self.activeWindows["Connect"][1])
        self.mLayout.addWidget(self.activeWindows["Test"][1])
        self.mLayout.addWidget(self.activeWindows["Board"][1])
        self.activeWindows["Test"][1].hide()
        self.activeWindows["Board"][1].hide()

        mWidget = QWidget()
        mWidget.setLayout(self.mLayout)
        self.setCentralWidget(mWidget)

    def test(self):
        self.switchWindow("Test")

    def connect(self):
        self.switchWindow("Connect")

    def board(self):
        self.switchWindow("Board")

    def switchWindow(self, window):
        for w in self.activeWindows:
            if w == window and not self.activeWindows[w][0]:
                self.activeWindows[w][1].show()
                self.activeWindows[w][0] = True
            elif w != window and self.activeWindows[w][0]:
                self.activeWindows[w][1].hide()
                self.activeWindows[w][0] = False


def startWindow():
    if hasattr(QtCore.Qt, 'AA_EnableHighDpiScaling'):
        PyQt5.QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)

    if hasattr(QtCore.Qt, 'AA_UseHighDpiPixmaps'):
        PyQt5.QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)
    app = QApplication(sys.argv + ['-platform', 'windows:darkmode=1'])
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())