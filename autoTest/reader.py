from lark import Lark, Transformer

with open("autotest/grammar.lark") as f:
    grammar = f.read()

lParser = Lark(grammar, start="start")

def parse(filename):
    with open(filename) as file:
        return lParser.parse(file.read())

class AbortExecution(Exception):
    pass

class Runner(Transformer):
    def __init__(self):
        super().__init__()
        self.abortFlag = False

    def set_throttle(self, args):
        self.checkAbort()
        throttle, = args
        print(f"Setting throttle {throttle}")

    def read_cell_1(self, _):
        self.checkAbort()
        print("Reading cell1")

    def read_cell_2(self, _):
        self.checkAbort()
        print("Reading cell2")

    def read_current(self, _):
        self.checkAbort()
        print("Reading current")

    def read_voltage(self, _):
        self.checkAbort()
        print("Reading voltage")

    def wait(self, args):
        self.checkAbort()
        milliseconds, = args
        print(f"Waiting for throttle {milliseconds} milliseconds...")

    def use_spreadsheet(self, args):
        self.checkAbort()
        print("Using spreadsheet")

    def write_sheet_cell(self, args):
        self.checkAbort()
        value, x, y = args
        print(f"Writing {value} to sheet cell {x} and {y}")

    def add_point(self, _):
        self.checkAbort()
        print("Adding point")

    def checkAbort(self):
        if self.abortFlag:
            raise AbortExecution("User Abort")