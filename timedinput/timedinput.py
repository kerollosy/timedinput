"""Timeout for python inputs"""

import sys
import time

if sys.platform.startswith("win"):
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

def is_jupyter():
    """Detects if the code is running inside a Jupyter Notebook, Google Colab, or IPython."""
    if 'google.colab' in sys.modules:
        return True
    
    try:
        shell = get_ipython().__class__.__name__
        if shell in ('ZMQInteractiveShell', 'Shell'):
            return True
        return False
    except NameError:
        return False

def jupyter_timedinput(prompt='', timeout=DEFAULT_TIMEOUT, default=None):
    """Timed input for Jupyter using jupyter_ui_poll."""
    import ipywidgets as widgets
    from IPython.display import display
    from jupyter_ui_poll import ui_events

    result = [None]
    done = [False]

    label = widgets.Label(value=prompt)
    
    # Add continuous_update=False so it only triggers on Enter
    text = widgets.Text(placeholder='Type and press Enter...', continuous_update=False)
    box = widgets.VBox([label, text])

    # The callback now receives a 'change' dictionary instead of the widget itself
    def on_submit(change):
        result[0] = change['new'] # Grab the newly typed text
        done[0] = True

    # Use observe to watch for changes to the 'value'
    text.observe(on_submit, names='value')
    display(box)

    start_time = time.monotonic()

    with ui_events() as poll:
        while not done[0]:
            poll(10)
            if time.monotonic() - start_time > timeout:
                break
            time.sleep(0.05)

    box.close()

    if not done[0]:
        if default is not None:
            return default
        raise TimeoutOccurred

    return result[0]


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

    if default is not None:
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
    if default is not None:
        return default
    raise TimeoutOccurred

def _fallback_timedinput(prompt='', timeout=DEFAULT_TIMEOUT, default=None):
    """Fallback that consumes extra arguments but acts like standard input"""
    return input(prompt)

if is_jupyter():
    try:
        import ipywidgets
        import jupyter_ui_poll
        timedinput = jupyter_timedinput
    except ImportError:
        import warnings
        warnings.warn(
            "For timeout support in Jupyter, you must install optional dependencies. "
            "Run: %pip install ipywidgets jupyter-ui-poll. "
            "Falling back to standard blocking input (no timeout)."
        )
        timedinput = _fallback_timedinput
elif sys.platform.startswith("win"):
    timedinput = win_timedinput
else:
    timedinput = posix_timedinput