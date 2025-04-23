import serial.tools.list_ports

from PyQt5.QtCore import QThread, pyqtSignal, QSize
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QFrame, QPushButton, QHBoxLayout, QWidget, QVBoxLayout, QLabel, QComboBox, QPlainTextEdit


class Connect(QFrame):
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

        topLayout.setContentsMargins(5, 0, 0, 0)
        mainLayout.setContentsMargins(10, 15, 10, 10)

    def connect(self):
        self.serialMonitor.connectReader(self.comPortSelector.combo.currentText(), 9600)


class SerialReaderThread(QThread):
    """
    Mostly vibecoded lol
    """
    data_received = pyqtSignal(str)

    def __init__(self, port: str, baudrate: int = 9600):
        super().__init__()
        self.port = port
        self.baudrate = baudrate
        self._running = True
        self.ser = None

    def run(self):
        """
        Thread loop: opens serial port and emits each received line.
        """
        try:
            self.ser = serial.Serial(self.port, self.baudrate, timeout=1)
        except serial.SerialException as e:
            # handle error (port unavailable, etc.)
            self.data_received.emit(f"Error opening serial port {self.port}: {e}")
            return

        while self._running:
            try:
                if self.ser.in_waiting:
                    line = self.ser.readline().decode('utf-8', errors='replace')
                    self.data_received.emit(line)
            except Exception as e:
                print(f"Serial read error: {e}")
                break

    def stop(self):
        """
        Cleanly stop the thread and close the serial port.
        """
        self._running = False
        if self.ser and self.ser.is_open:
            self.ser.close()
        self.quit()
        self.wait()


class SerialMonitorWidget(QWidget):
    """
    50% good vibes (vibecoded), 50% bad vibes (had to do it myself)
    """
    def __init__(self):
        super().__init__()

        # Layout and read-only text area
        layout = QVBoxLayout(self)
        self.textbox = QPlainTextEdit()
        self.textbox.setReadOnly(True)
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