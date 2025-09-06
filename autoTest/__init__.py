from PyQt5.QtCore import QThread

from . import reader
from .reference import RunnerThread

scriptRunning = False
runnerThread: RunnerThread | None = None

def runScript(script, addPoint, scriptComplete):
    global scriptRunning
    global runnerThread

    scriptRunning = True

    runnerThread = RunnerThread(script, scriptComplete, addPoint)
    runnerThread.start()

def cancelScript():
    global scriptRunning
    global runnerThread

    runnerThread.stop()

class RunnerThread(QThread):
    def __init__(self, script, scriptComplete, addPoint):
        QThread.__init__(self)

        self.script = script
        self.scriptComplete = scriptComplete
        self.addPoint = addPoint
        self.runner = None

        self.running = False

    def run(self):
        global scriptRunning

        self.running = True
        tree = reader.parse(self.script)
        self.runner = reader.Runner(self.addPoint)
        try:
            self.runner.transform(tree)
        except reader.AbortExecution:
            pass
        self.scriptComplete()
        scriptRunning = False
        self.running = False

    def stop(self):
        self.runner.abortFlag = True
        self.running = False