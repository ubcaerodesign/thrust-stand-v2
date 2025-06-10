import serial.tools.list_ports

from PyQt5.QtCore import QThread, pyqtSignal, QSize
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QFrame, QPushButton, QHBoxLayout, QWidget, QVBoxLayout, QLabel, QComboBox, QPlainTextEdit, \
    QLineEdit

from serial import SerialException

import board


class Connect(QFrame):
    # TODO: it is possible to connect to the same serial port multiple times resulting in incomprehensible data
    def __init__(self):
        super().__init__()

        # set stylesheet
        qss = "resources/dark.qss"
        with open(qss, "r") as f:
            self.setStyleSheet(f.read())

        iconBtnQss = "resources/iconBtn.qss"
        iconBtnStyle = None
        with open(iconBtnQss, "r") as f:
            iconBtnStyle = f.read()

        # split into two sections, top control bar and bottom console
        mainLayout = QVBoxLayout(self)
        topLayout = QHBoxLayout()

        # top control bar including the com port selector, refresh, and connect buttons
        self.comPortSelector = ComPortSelector()
        topLayout.addWidget(self.comPortSelector)

        refreshBtn = QPushButton()
        refreshIcon = QIcon("icons/refresh.png")
        refreshBtn.setIcon(refreshIcon)
        refreshBtn.setIconSize(QSize(18, 18))
        refreshBtn.setStyleSheet(iconBtnStyle)
        refreshBtn.clicked.connect(self.comPortSelector.refresh_ports)
        topLayout.addWidget(refreshBtn)

        connectBtn = QPushButton()
        connectIcon = QIcon("icons/connect.png")
        connectBtn.setIcon(connectIcon)
        connectBtn.setIconSize(QSize(20, 20))
        connectBtn.setStyleSheet(iconBtnStyle)
        connectBtn.clicked.connect(self.connect)
        topLayout.addWidget(connectBtn)

        topLayout.addStretch()
        mainLayout.addLayout(topLayout)

        # console that dumps all serial communication for debugging
        self.serialMonitor = SerialMonitorWidget()
        mainLayout.addWidget(self.serialMonitor)

        # input console
        self.serialCommand = SerialCommandSender(self.serialMonitor.appendUserCommand)
        mainLayout.addWidget(self.serialCommand)

        topLayout.setContentsMargins(5, 0, 0, 0)
        mainLayout.setContentsMargins(10, 15, 10, 10)

    def connect(self):
        self.serialMonitor.connectReader(self.comPortSelector.combo.currentText(), 9600)


class SerialReaderThread(QThread):
    """
    Somewhat vibecoded lol
    """
    data_received = pyqtSignal(str)

    def __init__(self, port: str, baudrate: int = 9600):
        super().__init__()
        self.port = port
        self.baudrate = baudrate
        self._running = True

    def run(self):
        """
        Thread loop: opens serial port and emits each received line.
        """
        if board.connect(self.port, self.baudrate):
            self.data_received.emit(f"Connected to serial port {self.port}")
        else:
            self.data_received.emit(f"Error opening serial port {self.port}")

        while self._running:
            try:
                line = board.getLine()
                if line is not None:
                    self.data_received.emit(line)
            except SerialException:
                self.data_received.emit("COM port disconnected")

    def stop(self):
        """
        Cleanly stop the thread and close the serial port.
        """
        self._running = False
        board.disconnect()
        self.quit()
        self.wait()


class SerialCommandSender(QWidget):
    def __init__(self, commandTracker):
        super().__init__()

        self.commandTracker = commandTracker

        self.layout = QHBoxLayout(self)

        self.prompt = QLabel(">")
        self.command_input = QLineEdit()
        self.command_input.returnPressed.connect(self.send_command)
        self.send_button = QPushButton("Send")
        self.send_button.setFixedHeight(31)
        self.send_button.setObjectName("greenBtn")
        self.send_button.clicked.connect(self.send_command)

        self.layout.addWidget(self.prompt)
        self.layout.addWidget(self.command_input)
        self.layout.addWidget(self.send_button)

    def send_command(self):
        command = self.command_input.text().strip()
        board.sendCommand(command)
        self.commandTracker(command)
        self.command_input.clear()


class SerialMonitorWidget(QWidget):
    # TODO: implement scrolling logic that stops autoscrolling when manually scrolling using scroll wheel
    # TODO: implement limit on amount of console lines possible
    # TODO: implement a command prompt style setup to directly address the arduino
    # TODO: implement a filter to hide all arduino data transmissions
    # TODO: implement a function to change polling rate on arduino
    """
    50% good vibes (vibecoded), 50% bad vibes (had to do it myself)
    """
    def __init__(self):
        super().__init__()

        # Layout and read-only text area
        layout = QVBoxLayout(self)
        self.textbox = QPlainTextEdit()
        self.textbox.setReadOnly(True)
        self.textbox.setObjectName("console")
        layout.addWidget(self.textbox)

        # Create reader variable
        self.reader = None

        # Autoscroll control
        self.autoscroll = True
        self.textbox.verticalScrollBar().sliderMoved.connect(self.scrollBarMoved)

    def connectReader(self, port, baudrate):
        """
        Connects the reader to the serial port.
        """
        self.reader = SerialReaderThread(port, baudrate)
        self.reader.data_received.connect(self.appendText)
        self.reader.start()

    def appendUserCommand(self, command: str):
        self.appendText(">" + command)

    def appendText(self, text: str):
        """
        Append received text to the textbox, scrolling to the end.
        """
        self.textbox.appendPlainText(text.rstrip())
        # auto-scroll
        if self.autoscroll:
            cursor = self.textbox.textCursor()
            cursor.movePosition(cursor.End)
            self.textbox.setTextCursor(cursor)

    def closeEvent(self, event):
        """
        Ensure the thread is stopped when the widget is closed.
        """
        self.reader.stop()
        super().closeEvent(event)

    def scrollBarMoved(self):
        """
        Controls whether the auto-scrolling is on or off
        """
        self.autoscroll = False
        if self.textbox.verticalScrollBar().value() == self.textbox.verticalScrollBar().maximum():
            self.autoscroll = True


class ComPortSelector(QWidget):
    def __init__(self):
        super().__init__()

        mLayout = QHBoxLayout(self)

        # Label + ComboBox
        lbl = QLabel("COM Port:")
        self.combo = QComboBox()
        mLayout.addWidget(lbl)
        mLayout.addWidget(self.combo)

        self.refresh_ports()

    def refresh_ports(self):
        """
        Populate the combo box with available serial ports.
        """
        ports = [port.device for port in serial.tools.list_ports.comports()]
        self.combo.clear()
        self.combo.addItems(ports)
        if ports:
            self.combo.setCurrentIndex(0)