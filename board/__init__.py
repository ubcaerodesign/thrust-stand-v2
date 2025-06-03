import serial

from . import read

"""
offsetDict: mutable offset dictionary
cell1Received cell2Received currentReceived voltageReceived: pyqt signals that can be connected to
note: cell1 cell2 current voltage contains raw readings that is not affected by the offset variables
reader must be a QObject class in order to be compatible with the PyQt library
"""

COMPort = "COM0"

ser = None

offsetDict = {
    "cell1": 0,
    "cell2": 0,
    "current": 0,
    "voltage": 0
}

reader = read.SerialReader(offsetDict)

cell1Received = reader.cell1Received
cell2Received = reader.cell2Received
currentReceived = reader.currentReceived
voltageReceived = reader.voltageReceived

def connect(port: str, baudrate: int = 9600):
    global ser
    try:
        ser = serial.Serial(port, baudrate, timeout=1)
        return True
    except serial.SerialException:
        # handle error (port unavailable, etc.)
        return False

def disconnect():
    # TODO: implement a clean disconnect
    """
    reference code
    self._running = False
        if board.disconnect() and self.ser.is_open:
            self.ser.close()
        self.quit()
        self.wait()
    """
    pass

def getLine():
    """
    reads and updates all variables in config
    """
    if ser.in_waiting:
        line = ser.readline().decode('utf-8', errors='replace')
        reader.decode(line)
        return line
    else:
        return None

def zeroCell1():
    global offsetDict
    offsetDict["cell1"] = reader.cell1

def zeroCell2():
    global offsetDict
    offsetDict["cell2"] = reader.cell2

def zeroCurrent():
    global offsetDict
    offsetDict["current"] = reader.current

def zeroVoltage():
    global offsetDict
    offsetDict["voltage"] = reader.voltage