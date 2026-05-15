import time
import pytest
from unittest.mock import patch
from timedinput import timedinput, TimeoutOccurred


def delayed_input(*args, **kwargs):
    """Simulate a user staring at the screen and doing nothing."""
    time.sleep(10)
    return ""


@patch('builtins.input', delayed_input)
def test_noinput():
    # Will pause for 1 second, get interrupted by the timeout, and return "k"
    assert timedinput("??", timeout=1, default="k") == "k"


@patch('builtins.input', delayed_input)
def test_timeout():
    # Will pause for 1 second, get interrupted, and raise the exception
    with pytest.raises(TimeoutOccurred):
        timedinput("??", timeout=1)