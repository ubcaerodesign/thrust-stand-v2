import sys

from PyQt5.QtWidgets import QMainWindow, QApplication, QHBoxLayout, QWidget

from .navbar import NavBar
from .connect import Connect

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AeroThrust")
        self.setMinimumSize(800, 600)
        self.resize(800, 600)

        mLayout = QHBoxLayout()
        mLayout.setContentsMargins(0, 0, 0, 0)
        mLayout.setSpacing(0)

        sidebar = NavBar()
        mLayout.addWidget(sidebar)

        connect = Connect()
        mLayout.addWidget(connect)

        mWidget = QWidget()
        mWidget.setLayout(mLayout)
        self.setCentralWidget(mWidget)

def startWindow():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())