from PyQt5.QtWidgets import QFrame, QVBoxLayout, QPushButton

from .themeManager import themeManager


class Settings(QFrame):
    def __init__(self):
        super().__init__()

        # setup stylesheet
        self.setStyleSheet(themeManager.getThemeStylesheet())
        themeManager.themeChanged.connect(self.setTheme)

        mainLayout = QVBoxLayout()

        switchThemeButton = QPushButton("Switch Theme")
        mainLayout.addWidget(switchThemeButton)
        switchThemeButton.clicked.connect(self.switchTheme)

        self.setLayout(mainLayout)

    def setTheme(self, stylesheet):
        self.setStyleSheet(stylesheet)

    def switchTheme(self):
        if themeManager.getThemeName() == "light":
            qss = "resources/dark.qss"
            with open(qss, "r") as f:
                stylesheet = f.read()
                themeManager.setTheme("dark", stylesheet)
        elif themeManager.getThemeName() == "dark":
            qss = "resources/light.qss"
            with open(qss, "r") as f:
                stylesheet = f.read()
                themeManager.setTheme("light", stylesheet)