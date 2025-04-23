import serial

import config
import read

def connect(port: str, baudrate: int = 9600):
    config.ser = serial.Serial(port, baudrate, timeout=1)

def disconnect():
    pass

def getLine():
    """
    reads and updates all variables in config
    """
    line = config.ser.readline().decode('utf-8', errors='replace')
    read.decode(line)
    return line