from . import config

def zeroThrust():
    config.thrustOffset = config.cell1

def zeroTorque():
    config.torqueOffset = config.cell2

def zeroCurrent():
    config.currentOffset = config.current

def zeroVoltage():
    config.voltageOffset = config.voltage