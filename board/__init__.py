# TODO: considering restructuring data out of config to make a cleaner package

import serial

from . import config
from . import read

config.readQThread = read.SerialReaderThread()

def connect(port: str, baudrate: int = 9600):
    try:
        config.ser = serial.Serial(port, baudrate, timeout=1)
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
    if config.ser.in_waiting:
        line = config.ser.readline().decode('utf-8', errors='replace')
        config.readQThread.decode(line)
        return line
    else:
        return None