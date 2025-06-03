import re

from PyQt5.QtCore import pyqtSignal, QObject


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


class SerialReader(QObject):
    cell1 = 0
    cell2 = 0
    voltage = 0
    current = 0

    cell1Received = pyqtSignal(int)
    cell2Received = pyqtSignal(int)
    currentReceived = pyqtSignal(float)
    voltageReceived = pyqtSignal(float)

    def __init__(self, offsetDict):
        super().__init__()

        self.offsetDict = offsetDict

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
            self.cell1 = _parse_long_or_none(line)
            if self.cell1 is not None:
                self.cell1Received.emit(self.cell1 - self.offsetDict["cell1"])
        elif line.startswith("lc2("):
            self.cell2 = _parse_long_or_none(line)
            if self.cell2 is not None:
                self.cell2Received.emit(self.cell2 - self.offsetDict["cell2"])
        elif line.startswith("cur("):
            self.current = _parse_float(line)
            if self.current is not None:
                self.currentReceived.emit(round(self.current - self.offsetDict["current"], 2))
        elif line.startswith("vtg("):
            self.voltage = _parse_float(line)
            if self.voltage is not None:
                self.voltageReceived.emit(round(self.voltage - self.offsetDict["voltage"], 2))

