"""Timeout for python inputs"""

import sys

if sys.platform.startswith("win"):
    import time
    import msvcrt
else:
    import selectors
    import termios


DEFAULT_TIMEOUT = 30.0
INTERVAL = 0.05

SP = ' '
CR = '\r'
LF = '\n'
CRLF = CR + LF


class TimeoutOccurred(Exception):
    """Gets raised when user doesn't enter
    any input within the specified timeout and no default value is specified"""


def echo(string):
    """Prints a string"""
    sys.stdout.write(string)
    sys.stdout.flush()


def posix_timedinput(prompt='', timeout=DEFAULT_TIMEOUT, default=None):
    """Timedinput for Unix operating systems"""
    echo(prompt)
    sel = selectors.DefaultSelector()
    sel.register(sys.stdin, selectors.EVENT_READ)
    events = sel.select(timeout)

    if events:
        key, _ = events[0]
        return key.fileobj.readline().rstrip(LF)

    echo(LF)
    termios.tcflush(sys.stdin, termios.TCIFLUSH)

    if default:
        return default
    raise TimeoutOccurred


def win_timedinput(prompt='', timeout=DEFAULT_TIMEOUT, default=None):
    """Timedinput for Windows operating systems"""
    echo(prompt)
    begin = time.monotonic()
    end = begin + timeout
    line = ''

    while time.monotonic() < end:
        if msvcrt.kbhit():
            c = msvcrt.getwche()

            # User pressed Enter
            if c in (CR, LF):
                echo(CRLF)
                return line

            # User pressed ^C (CTRL+C)
            if c == '\003':
                raise KeyboardInterrupt

            # User pressed Backspace
            if c == '\b':
                line = line[:-1]
                cover = SP * len(prompt + line + SP)
                echo(''.join([CR, cover, CR, prompt, line]))

            else:
                line += c
        time.sleep(INTERVAL)

    echo(CRLF)
    if default:
        return default
    raise TimeoutOccurred


if sys.platform.startswith("win"):
    timedinput = win_timedinput
else:
    timedinput = posix_timedinput
