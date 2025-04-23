# entire file is vibecoded

import config

import re

def decode(line):
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
    elif line.startswith("lc2("):
        config.cell2 = _parse_long_or_none(line)
    elif line.startswith("cur("):
        config.current = _parse_float(line)
    elif line.startswith("vtg("):
        config.voltage = _parse_float(line)

def _parse_long_or_none(line):
    """
    Parses long integer or 'n' from a line like 'lc1(1234)' or 'lc1(n)'
    """
    match = re.match(r".*\((n|\d+)\)", line)
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