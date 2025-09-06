import sys, traceback

from PyQt5 import QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QSplashScreen

def excepthook(exc_type, exc_value, exc_tb):
    # print the full Python traceback
    traceback.print_exception(exc_type, exc_value, exc_tb)
    # call the default handler in case Qt/IDE needs it
    sys.__excepthook__(exc_type, exc_value, exc_tb)

def startWindow():
    """
    Shows a splash screen while dynamically importing all modules in the main app
    """

    # rescale ui for laptops
    """if hasattr(QtCore.Qt, 'AA_EnableHighDpiScaling'):
        QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)"""

    """if hasattr(QtCore.Qt, 'AA_UseHighDpiPixmaps'):
        QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)"""
    app = QApplication(sys.argv + ['-platform', 'windows:darkmode=1'])
    sys.excepthook = excepthook

    # loading screen
    pixmap = QPixmap("icons/loading-screen.png")
    splash = QSplashScreen(pixmap)
    splash.showMessage("..........  Loading  ..........", Qt.AlignCenter | Qt.AlignBottom, Qt.white)
    splash.show()
    app.processEvents()

    # actual window
    from . import window
    window = window.MainWindow()
    splash.finish(window)
    window.show()
    sys.exit(app.exec_())