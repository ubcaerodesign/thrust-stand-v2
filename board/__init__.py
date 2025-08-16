import serial

from typing import Optional

from . import read

"""
offsetDict: mutable offset dictionary
cell1Received cell2Received currentReceived voltageReceived: pyqt signals that can be connected to
note: cell1 cell2 current voltage contains raw readings that is not affected by the offset variables
reader must be a QObject class in order to be compatible with the PyQt library
"""

COMPort = "COM0"

ser: Optional[serial.Serial] = None

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
    if ser.is_open:
        ser.close()
        return True
    return False

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

def setThrottle(throttle: int):
    if throttle < 0 or throttle > 100:
        raise ValueError("throttle must be between 0 and 100")
    sendCommand(f"thr({throttle})")

def sendCommand(command: str):
    if ser and ser.is_open:
        try:
            ser.write((command + "\n").encode('utf-8'))
            return True
        except Exception:
            return False
    else:
        return False