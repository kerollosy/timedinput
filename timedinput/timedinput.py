"""Timeout for python inputs"""

import sys
import time
import warnings

if sys.platform.startswith("win"):
    import msvcrt
else:
    import readline  # noqa: F401 - readline is imported for its side effects on Unix
    import signal
    import termios


DEFAULT_TIMEOUT = 30.0
INTERVAL = 0.05

SP = ' '
CR = '\r'
LF = '\n'
CRLF = CR + LF


class TimeoutOccurred(Exception):
    """Raised when the user doesn't enter input within the specified timeout
    and no default value was provided."""


def is_jupyter():
    """Detects if the code is running inside a Jupyter Notebook, Google Colab, or IPython."""
    if 'google.colab' in sys.modules:
        return True

    try:
        shell = get_ipython() # noqa: F821 - get_ipython is a special function available in IPython environments
        if shell is None:
            return False
        
        return shell.__class__.__name__ in ('ZMQInteractiveShell', 'Shell')
    except Exception:
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
                done[0] = False
                break
            time.sleep(0.05)

    box.close()

    if not done[0]:
        if default is not None:
            return default
        raise TimeoutOccurred

    return result[0]


def _timeout_handler(signum, frame):
    """Signal handler that raises a timeout exception."""
    raise TimeoutOccurred()


def posix_timedinput(prompt='', timeout=5, default=None):
    """Timedinput for Unix operating systems"""
    old_handler = signal.signal(signal.SIGALRM, _timeout_handler)
    
    try:
        signal.setitimer(signal.ITIMER_REAL, timeout)
        result = input(prompt)
        return result

    except TimeoutOccurred:
        print()

        try:
            termios.tcflush(sys.stdin, termios.TCIFLUSH)
        except Exception:
            pass
            
        if default is not None:
            return default
        raise
        
    except EOFError:
        print()
        raise
        
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
        signal.signal(signal.SIGALRM, old_handler)


def echo(string):
    """Prints a string without a newline and flushes stdout immediately."""
    print(string, end="", flush=True)


def win_timedinput(prompt='', timeout=DEFAULT_TIMEOUT, default=None):
    """Timedinput for Windows operating systems"""
    echo(prompt)
    begin = time.monotonic()
    end = begin + timeout
    line = ''
    pos = 0  # cursor position within line

    def redraw():
        # Reprint line from start, trailing ' \b' erases any leftover character
        echo('\r' + prompt + line + ' \b')
        back = len(line) - pos
        if back:
            echo('\b' * back)

    while time.monotonic() < end:
        if msvcrt.kbhit():
            c = msvcrt.getwch()

            if c in ('\x00', '\xe0'):
                scan = msvcrt.getwch()
                if scan == '\x4b' and pos > 0:            # Left arrow
                    pos -= 1
                    echo('\b')
                elif scan == '\x4d' and pos < len(line):  # Right arrow
                    echo(line[pos])
                    pos += 1
                elif scan == '\x47':                       # Home
                    echo('\b' * pos)
                    pos = 0
                elif scan == '\x4f':                       # End
                    echo(line[pos:])
                    pos = len(line)
                elif scan == '\x53' and pos < len(line):  # Delete key
                    line = line[:pos] + line[pos + 1:]
                    redraw()
                continue

            # User pressed Enter
            if c in (CR, LF):
                echo(CRLF)
                return line

            # User pressed ^C (CTRL+C)
            if c == '\003':
                raise KeyboardInterrupt

            # User pressed Backspace
            if c == '\b':
                if pos > 0:
                    line = line[:pos - 1] + line[pos:]
                    pos -= 1
                    redraw()
            else:
                line = line[:pos] + c + line[pos:]
                pos += 1
                redraw()

        time.sleep(INTERVAL)

    echo(CRLF)
    if default is not None:
        return default
    raise TimeoutOccurred


def _fallback_timedinput(prompt='', _timeout=DEFAULT_TIMEOUT, _default=None):
    """Fallback that consumes extra arguments but acts like standard input"""
    return input(prompt)


def timedinput(prompt='', timeout=DEFAULT_TIMEOUT, default=None):
    """Prompt the user for input with an optional timeout.

    Automatically selects the correct implementation for the current platform
    (Windows, POSIX, or Jupyter). If the user doesn't respond within the
    timeout, either returns ``default`` or raises ``TimeoutOccurred``.

    Args:
        prompt (str): Message displayed before the input cursor. Defaults to ''.
        timeout (float): Seconds to wait for input before timing out.
            Defaults to 30.0.
        default: Value to return if the timeout expires. If None and the
            timeout expires, raises TimeoutOccurred. Defaults to None.

    Returns:
        str: The text entered by the user, or ``default`` if timed out.

    Raises:
        TimeoutOccurred: If the timeout expires and no default is provided.
        KeyboardInterrupt: If the user presses Ctrl+C (Windows).
        EOFError: If stdin is closed unexpectedly (POSIX).

    Examples:
        >>> answer = timedinput("Continue? [Y/n]: ", timeout=5, default="Y")
        >>> name = timedinput("Enter your name: ", timeout=10)
    """
    if is_jupyter():
        try:
            return jupyter_timedinput(prompt, timeout, default)
        except ImportError:
            warnings.warn(
                "For timeout support in Jupyter, install optional dependencies: "
                "%pip install ipywidgets jupyter-ui-poll. "
                "Falling back to standard blocking input (timeout and default ignored).",
                stacklevel=2,
            )
            return _fallback_timedinput(prompt, timeout, default)

    if sys.platform.startswith("win"):
        return win_timedinput(prompt, timeout, default)

    return posix_timedinput(prompt, timeout, default)


answer = timedinput("Continue? [Y/n]: ", timeout=5, default="Y")
print(f"You entered: {answer}")