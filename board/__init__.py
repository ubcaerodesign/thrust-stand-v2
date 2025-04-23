import serial

from . import config
from . import read

def connect(port: str, baudrate: int = 9600):
    try:
        config.ser = serial.Serial(port, baudrate, timeout=1)
        return True
    except serial.SerialException as e:
        # handle error (port unavailable, etc.)
        return False

def disconnect():
    pass

def getLine():
    """
    reads and updates all variables in config
    """
    if config.ser.in_waiting:
        line = config.ser.readline().decode('utf-8', errors='replace')
        read.decode(line)
        return line
    else:
        return None