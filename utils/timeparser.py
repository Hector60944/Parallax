import re
import time as date  # Note: time.time() is UTC seconds from Jan 1 1970
from datetime import datetime


TIMES = {
    's': 1,
    'm': 60,
    'h': 3600,
    'd': 86400,
    'w': 604800
}

SHORT_UNITS = {
    's': 'second',
    'm': 'minute',
    'h': 'hour',
    'd': 'day',
    'w': 'week'
}

SHORT_TIME_RX = re.compile('^[0-9]+[smhdw]', re.IGNORECASE)
LONG_TIME_RX = re.compile('^([0-9]+) *(s(?:ec(?:ond(?:s)?)?)?|m(?:in(?:ute(?:s)?)?)?|h(?:our(?:s)?)?|d(?:ay(?:s)?)?|w(?:eek(?:s)?)?)', re.IGNORECASE)


class TimeFormat:
    def __init__(self, absolute: int, relative: int, amount: int, unit: str, human: str):
        self.absolute = absolute
        self.relative = relative
        self.amount = amount
        self.unit = unit
        self.humanized = human

    def __str__(self):
        return f'{self.amount} {self.unit}'


def convert(text: str):
    match = SHORT_TIME_RX.search(text)

    if not match:
        return None, text

    content = match.group()
    start = match.span()[1]

    time = int(content[:-1])
    unit = content[-1].lower()
    formal_unit = f'{SHORT_UNITS[unit]}{"s" if time != 1 else ""}'

    relative = TIMES[unit] * time
    absolute = int(round(date.time())) + relative
    human = datetime.fromtimestamp(absolute).strftime("%d-%m-%y %H:%M:%S")

    return TimeFormat(absolute, relative, time, formal_unit, human), text[start:].strip()


def parse(text: str):
    match = LONG_TIME_RX.match(text)

    if not match:
        return None

    time = int(match.group(1))
    unit = match.group(2).lower()[0]

    relative = TIMES[unit] * time
    absolute = int(round(date.time())) + relative
    human = datetime.fromtimestamp(absolute).strftime("%d-%m-%y %H:%M:%S")

    return TimeFormat(absolute, relative, time, unit, human)
