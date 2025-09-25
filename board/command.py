from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot, QThread

class SerialWorker(QObject):
    sendCommandSignal = pyqtSignal(str)  # new throttle value

    def __init__(self, serialPort):
        super().__init__()
        self.serialPort = serialPort
        self.sendCommandSignal.connect(self.writeThrottle)

    @pyqtSlot(str)
    def writeThrottle(self, msg):
        if self.serialPort and self.serialPort.is_open:
            try:
                self.serialPort.write((msg + "\n").encode('utf-8'))
                return True
            except Exception:
                return False
        else:
            return False
