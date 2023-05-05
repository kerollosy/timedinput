import pytest
from timedinput import timedinput, TimeoutOccurred


def test_noinput():
    assert timedinput("??", 1, "k") == "k"


def test_timeout():
    with pytest.raises(TimeoutOccurred):
        timedinput("??", 1)
