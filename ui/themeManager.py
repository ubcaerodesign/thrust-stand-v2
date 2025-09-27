from PyQt5.QtCore import QObject, pyqtSignal

class ThemeManager(QObject):
    themeChanged = pyqtSignal(str)  # emit the stylesheet string

    def __init__(self):
        super().__init__()
        self.theme = "dark"
        self.stylesheet = ""

    def setTheme(self, themeName, stylesheet):
        self.theme = themeName
        self.stylesheet = stylesheet
        self.themeChanged.emit(stylesheet)

    def getThemeStylesheet(self):
        return self.stylesheet

    def getThemeName(self):
        return self.theme


themeManager = ThemeManager()