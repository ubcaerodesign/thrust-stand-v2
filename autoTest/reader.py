from lark import Lark, Transformer

import board

with open("autotest/grammar.lark") as f:
    grammar = f.read()

lParser = Lark(grammar, start="start")

def parse(filename):
    with open(filename) as file:
        return lParser.parse(file.read())

class AbortExecution(Exception):
    pass

class Runner(Transformer):
    def __init__(self, addPoint):
        super().__init__()

        self.addPoint = addPoint
        self.abortFlag = False
        self.useRaw = False

    def set_throttle(self, args):
        self.checkAbort()
        throttle, = args
        print(f"Setting throttle {throttle}")

    def read_cell_1(self, _):
        self.checkAbort()
        if self.useRaw:
            return board.reader.cell1
        return board.reader.cell1 - board.offsetDict["cell1"]

    def read_cell_2(self, _):
        self.checkAbort()
        if self.useRaw:
            return board.reader.cell2
        return board.reader.cell2 - board.offsetDict["cell2"]

    def read_current(self, _):
        self.checkAbort()
        if self.useRaw:
            return board.reader.current
        return board.reader.current - board.offsetDict["current"]

    def read_voltage(self, _):
        self.checkAbort()
        if self.useRaw:
            return board.reader.voltage
        return board.reader.voltage - board.offsetDict["voltage"]

    def wait(self, args):
        self.checkAbort()
        milliseconds, = args
        print(f"Waiting for throttle {milliseconds} milliseconds...")

    def use_raw(self, args):
        self.checkAbort()
        rawBool = args[0]
        self.useRaw = rawBool.lower() == "true"

    def use_spreadsheet(self, args):
        self.checkAbort()
        print("Using spreadsheet")

    def write_sheet_cell(self, args):
        self.checkAbort()
        value, x, y = args
        print(f"Writing {value} to sheet cell {x} and {y}")

    def add_point(self, _):
        self.checkAbort()
        self.addPoint()

    def checkAbort(self):
        if self.abortFlag:
            raise AbortExecution("User Abort")