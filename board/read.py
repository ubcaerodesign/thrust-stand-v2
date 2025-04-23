import re

from PyQt5.QtCore import pyqtSignal, QObject

from . import config


def _parse_long_or_none(line):
    """
    Parses long integer or 'n' from a line like 'lc1(1234)', 'lc1(-49)' or 'lc1(n)'
    """
    match = re.match(r".*\((n|-?\d+)\)", line)
    if match:
        val = match.group(1)
        return None if val == 'n' else int(val)
    return None


def _parse_float(line):
    """
    Parses float value from a line like 'cur(3.45)'
    """
    match = re.match(r".*\(([-+]?[0-9]*\.?[0-9]+)\)", line)
    if match:
        return float(match.group(1))
    return None


# TODO: rename this class as this is not actually a thread
class SerialReaderThread(QObject):
    cell1Received = pyqtSignal(int)
    cell2Received = pyqtSignal(int)
    currentReceived = pyqtSignal(float)
    voltageReceived = pyqtSignal(float)

    def __init__(self):
        super().__init__()

    def decode(self, line: str):
        """
        Decodes a single line of serial input and updates config values.
        Expected formats:
        - lc1(<long>|n)
        - lc2(<long>|n)
        - cur(<float>)
        - vtg(<float>)
        """
        if line.startswith("lc1("):
            config.cell1 = _parse_long_or_none(line)
            self.cell1Received.emit(config.cell1 - config.thrustOffset)
        elif line.startswith("lc2("):
            config.cell2 = _parse_long_or_none(line)
            self.cell2Received.emit(config.cell2 - config.torqueOffset)
        elif line.startswith("cur("):
            config.current = _parse_float(line)
            self.currentReceived.emit(round(config.current - config.currentOffset, 2))
        elif line.startswith("vtg("):
            config.voltage = _parse_float(line)
            self.voltageReceived.emit(round(config.voltage - config.voltageOffset, 2))

