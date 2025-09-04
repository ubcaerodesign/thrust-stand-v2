"""
PyQt5 + Lark DSL Demo

A single-file demo showing how to build and run a tiny testing DSL with Lark inside a PyQt5 GUI.

Dependencies:
    pip install PyQt5 lark

Run:
    python lark_pyqt5_dsl_demo.py

DSL overview:
    Commands end by newline (no semicolons needed). Comments start with '#'.

    SET_PWM <channel> <value>          -> set a PWM value (float/int)
    WAIT <seconds>                     -> sleep seconds (interruptible)
    READ_SENSOR <name>                 -> read a sensor (logs value)
    <VAR> = READ_SENSOR <name>         -> read and assign
    <VAR> = <expr>                     -> assign an expression
    IF <expr> THEN { ... } ELSE { ... }  -> conditional with blocks
    REPEAT <n> { ... }                 -> repeat block n times

    Expressions support + - * / and comparisons > < >= <= == !=

Example script (also available via the "Load Example" button):
    # spin motor, wait, read temp, branch, and repeat
    SET_PWM motor1 1200
    WAIT 1
    TEMP = READ_SENSOR temp
    IF TEMP > 40 THEN {
        SET_PWM fan 2000
    } ELSE {
        SET_PWM fan 1200
    }

    REPEAT 3 {
        SET_PWM servo 1500
        WAIT 0.2
        SET_PWM servo 1200
        WAIT 0.2
    }
"""

import sys
import time
from dataclasses import dataclass
from typing import Callable, List, Any, Dict

from PyQt5 import QtCore, QtWidgets
from lark import Lark, Transformer, Token, Tree

# ------------------------- Grammar -------------------------
GRAMMAR = r"""
?start: statement*

?statement: set_pwm
          | wait
          | read_stmt
          | assign
          | if_stmt
          | repeat
          | block   -> bare_block   // allow stray blocks (no-op)

set_pwm: "SET_PWM" NAME NUMBER            -> set_pwm
wait: "WAIT" NUMBER                      -> wait

// Two forms: bare read (just logs) or assignment read
read_stmt: "READ_SENSOR" NAME            -> read_sensor
         | NAME "=" "READ_SENSOR" NAME  -> read_assign

assign: NAME "=" expr                    -> assign

if_stmt: "IF" expr "THEN" block ("ELSE" block)? -> if_stmt

repeat: "REPEAT" NUMBER block             -> repeat

block: "{" statement* "}"

?expr: sum (comp_op sum)?               -> cmp
?sum: product (("+"|"-") product)*     -> fold_bin
?product: atom (("*"|"/") atom)*       -> fold_bin
?atom: NUMBER                           -> number
     | NAME                             -> var
     | "(" expr ")"

comp_op: ">="|"<="|">"|"<"|"=="|"!="

NAME: /[a-zA-Z_][a-zA-Z0-9_]*/
NUMBER: /-?\d+(\.\d+)?/

COMMENT: /#[^\n]*/
%ignore COMMENT
%import common.WS
%ignore WS
%import common.NEWLINE
%ignore NEWLINE
"""

# ------------------------- Engine (hardware stubs) -------------------------
@dataclass
class EngineCallbacks:
    log: Callable[[str], None]
    check_stop: Callable[[], bool]

class Engine:
    """Executes primitive operations (replace with real hardware I/O)."""
    def __init__(self, cbs: EngineCallbacks):
        self.vars: Dict[str, Any] = {}
        self._cbs = cbs

    # --- Helpers ---
    def _log(self, msg: str):
        self._cbs.log(msg)

    def _interruption_sleep(self, seconds: float):
        end = time.time() + float(seconds)
        # Sleep in short chunks so Stop works quickly
        while time.time() < end:
            if self._cbs.check_stop():
                raise KeyboardInterrupt("Execution stopped")
            time.sleep(min(0.05, end - time.time()))

    # --- Primitive ops ---
    def set_pwm(self, channel: str, value: float):
        self._log(f"[SET_PWM] channel={channel} value={value}")
        # TODO: hook to your real PWM driver here

    def wait(self, seconds: float):
        self._log(f"[WAIT] {seconds} s")
        self._interruption_sleep(seconds)

    def read_sensor(self, name: str) -> float:
        # TODO: replace with real sensor reading
        # For demo, return a pseudo value based on name/time
        base = sum(ord(c) for c in name) % 50
        value = float(base) + (time.time() % 10)  # changing-ish
        self._log(f"[READ_SENSOR] {name} = {value:.2f}")
        return value

# ------------------------- Builder Transformer -------------------------
class ProgramBuilder(Transformer):
    """Builds a list of zero-arg callables to run later against Engine."""
    def __init__(self, engine: Engine):
        super().__init__()
        self.E = engine

    # Terminals
    def NUMBER(self, t: Token):
        return float(t)

    def NAME(self, t: Token):
        return str(t)

    # Literals / expr
    def number(self, args):
        return args[0]

    def var(self, args):
        name = args[0]
        return ("VAR", name)

    def fold_bin(self, args):
        # args like: left, op, right, op, right, ...
        # We'll produce a thunk that when called computes the value from current vars
        def make_eval(parts):
            def eval_expr():
                def eval_atom(x):
                    if isinstance(x, tuple) and x[0] == "VAR":
                        return float(self.E.vars.get(x[1], 0.0))
                    return float(x)
                val = eval_atom(parts[0])
                i = 1
                while i < len(parts):
                    op = parts[i]
                    rhs = eval_atom(parts[i+1])
                    if op == "+":
                        val += rhs
                    elif op == "-":
                        val -= rhs
                    elif op == "*":
                        val *= rhs
                    elif op == "/":
                        val /= rhs
                    i += 2
                return val
            return eval_expr
        return make_eval(args)

    def cmp(self, args):
        # Either single value or (lhs, op, rhs)
        if len(args) == 1:
            # produce a thunk returning numeric value's truthiness
            ev_left = args[0]
            def cond():
                l = ev_left() if callable(ev_left) else (float(self.E.vars.get(ev_left[1], 0.0)) if isinstance(ev_left, tuple) else float(ev_left))
                return l != 0.0
            return cond
        lhs, op, rhs = args
        def cond():
            def eval_part(p):
                if callable(p):
                    return p()
                if isinstance(p, tuple) and p[0] == "VAR":
                    return float(self.E.vars.get(p[1], 0.0))
                return float(p)
            L = eval_part(lhs)
            R = eval_part(rhs)
            if op == ">":
                return L > R
            if op == "<":
                return L < R
            if op == ">=":
                return L >= R
            if op == "<=":
                return L <= R
            if op == "==":
                return L == R
            if op == "!=":
                return L != R
            return False
        return cond

    def comp_op(self, args):
        return str(args[0])

    # Statements -> callables
    def set_pwm(self, args):
        channel, value = args
        def run():
            if self.E._cbs.check_stop():
                raise KeyboardInterrupt
            self.E.set_pwm(channel, float(value))
        return run

    def wait(self, args):
        seconds = float(args[0])
        def run():
            if self.E._cbs.check_stop():
                raise KeyboardInterrupt
            self.E.wait(seconds)
        return run

    def read_sensor(self, args):
        name = args[0]
        def run():
            if self.E._cbs.check_stop():
                raise KeyboardInterrupt
            _ = self.E.read_sensor(name)
        return run

    def read_assign(self, args):
        varname, sensor_name = args
        def run():
            if self.E._cbs.check_stop():
                raise KeyboardInterrupt
            val = self.E.read_sensor(sensor_name)
            self.E.vars[varname] = float(val)
            self.E._log(f"[VAR] {varname} = {val}")
        return run

    def assign(self, args):
        varname, expr_ev = args
        def eval_expr():
            if callable(expr_ev):
                return float(expr_ev())
            if isinstance(expr_ev, tuple) and expr_ev[0] == "VAR":
                return float(self.E.vars.get(expr_ev[1], 0.0))
            return float(expr_ev)
        def run():
            if self.E._cbs.check_stop():
                raise KeyboardInterrupt
            val = eval_expr()
            self.E.vars[varname] = float(val)
            self.E._log(f"[VAR] {varname} = {val}")
        return run

    def block(self, stmts):
        # Return list of callables
        return [s for s in stmts if callable(s)]

    def bare_block(self, stmts):
        # A stray block by itself does nothing when executed
        def run():
            pass
        return run

    def if_stmt(self, args):
        cond = args[0]
        then_block = args[1] if isinstance(args[1], list) else [args[1]]
        else_block = args[2] if len(args) > 2 else []
        if not isinstance(else_block, list):
            else_block = [else_block]
        def run():
            take_then = cond() if callable(cond) else bool(cond)
            block = then_block if take_then else else_block
            for stmt in block:
                if self.E._cbs.check_stop():
                    raise KeyboardInterrupt
                stmt()
        return run

    def repeat(self, args):
        n, block = args
        if not isinstance(block, list):
            block = [block]
        n = int(float(n))
        def run():
            for _ in range(n):
                for stmt in block:
                    if self.E._cbs.check_stop():
                        raise KeyboardInterrupt
                    stmt()
        return run

    def start(self, stmts):
        # produce the top-level program: list of callables
        return [s for s in stmts if callable(s)]

# ------------------------- Worker Thread -------------------------
class RunnerThread(QtCore.QThread):
    log_signal = QtCore.pyqtSignal(str)
    done_signal = QtCore.pyqtSignal()
    error_signal = QtCore.pyqtSignal(str)

    def __init__(self, script: str, parent=None):
        super().__init__(parent)
        self.script = script
        self._stop = False

    def stop(self):
        self._stop = True

    def run(self):
        def log(msg: str):
            self.log_signal.emit(msg)
        def check_stop() -> bool:
            return self._stop
        engine = Engine(EngineCallbacks(log=log, check_stop=check_stop))
        try:
            parser = Lark(GRAMMAR, start="start", maybe_placeholders=False)
            program_tree = parser.parse(self.script)
            builder = ProgramBuilder(engine)
            program: List[Callable[[], None]] = builder.transform(program_tree)
            # Execute program
            for stmt in program:
                if self._stop:
                    raise KeyboardInterrupt("Stopped")
                stmt()
            self.done_signal.emit()
        except KeyboardInterrupt:
            self.log_signal.emit("\n[STOPPED] Execution interrupted by user.")
            self.done_signal.emit()
        except Exception as e:
            # Try to give line/column if it's a Lark error
            msg = str(e)
            if hasattr(e, 'line') and hasattr(e, 'column'):
                msg = f"Parse/Exec error at line {e.line}, column {e.column}: {e}"
            self.error_signal.emit(msg)

# ------------------------- PyQt5 GUI -------------------------
EXAMPLE_SCRIPT = """# spin motor, wait, read temp, branch, and repeat\nSET_PWM motor1 1200\nWAIT 1\nTEMP = READ_SENSOR temp\nIF TEMP > 40 THEN {\n    SET_PWM fan 2000\n} ELSE {\n    SET_PWM fan 1200\n}\n\nREPEAT 3 {\n    SET_PWM servo 1500\n    WAIT 0.2\n    SET_PWM servo 1200\n    WAIT 0.2\n}\n"""

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Lark DSL Test Runner")
        self.resize(980, 720)

        self.editor = QtWidgets.QPlainTextEdit()
        self.editor.setPlaceholderText("Write your test script here…")
        self.editor.setPlainText(EXAMPLE_SCRIPT)
        self.editor.setTabStopDistance(4 * self.editor.fontMetrics().horizontalAdvance(' '))

        self.log = QtWidgets.QTextEdit()
        self.log.setReadOnly(True)
        self.log.setPlaceholderText("Logs will appear here…")

        self.run_btn = QtWidgets.QPushButton("Run")
        self.stop_btn = QtWidgets.QPushButton("Stop")
        self.example_btn = QtWidgets.QPushButton("Load Example")

        self.stop_btn.setEnabled(False)

        btn_row = QtWidgets.QHBoxLayout()
        btn_row.addWidget(self.run_btn)
        btn_row.addWidget(self.stop_btn)
        btn_row.addStretch(1)
        btn_row.addWidget(self.example_btn)

        central = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(central)
        splitter = QtWidgets.QSplitter()
        splitter.setOrientation(QtCore.Qt.Vertical)
        splitter.addWidget(self.editor)
        splitter.addWidget(self.log)
        splitter.setStretchFactor(0, 3)
        splitter.setStretchFactor(1, 2)

        layout.addLayout(btn_row)
        layout.addWidget(splitter)
        self.setCentralWidget(central)

        self.run_btn.clicked.connect(self.on_run)
        self.stop_btn.clicked.connect(self.on_stop)
        self.example_btn.clicked.connect(self.on_example)

        self.runner: RunnerThread | None = None

    def on_example(self):
        self.editor.setPlainText(EXAMPLE_SCRIPT)
        self.log.clear()

    def on_run(self):
        if self.runner is not None and self.runner.isRunning():
            QtWidgets.QMessageBox.warning(self, "Busy", "A script is already running.")
            return
        self.log.clear()
        script = self.editor.toPlainText()
        self.runner = RunnerThread(script)
        self.runner.log_signal.connect(self.append_log)
        self.runner.done_signal.connect(self.on_done)
        self.runner.error_signal.connect(self.on_error)
        self.runner.start()
        self.run_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)

    def on_stop(self):
        if self.runner and self.runner.isRunning():
            self.runner.stop()

    def on_done(self):
        self.append_log("\n[DONE]")
        self.run_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)

    def on_error(self, msg: str):
        self.append_log(f"\n[ERROR] {msg}")
        self.run_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)

    @QtCore.pyqtSlot(str)
    def append_log(self, text: str):
        self.log.append(text)


def main():
    app = QtWidgets.QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
