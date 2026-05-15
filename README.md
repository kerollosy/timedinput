# timedinput 

[![PyPI version](https://img.shields.io/pypi/v/timedinput.svg)](https://pypi.org/project/timedinput/)
[![Python versions](https://img.shields.io/pypi/pyversions/timedinput.svg)](https://pypi.org/project/timedinput/)
[![Build status](https://img.shields.io/appveyor/build/kerollosy/timedinput.svg)](https://ci.appveyor.com/project/kerollosy/timedinput)
[![License](https://img.shields.io/github/license/kerollosy/timedinput.svg)](https://github.com/kerollosy/timedinput/blob/main/LICENSE)

A Python module that waits for a specified amount of time for user input. If no input is received within the given timeout period, the module returns a default value or raises an exception. 

Unlike standard timeout modules, `timedinput` actively monitors keystrokes and fully supports modern interactive environments like **Jupyter Notebooks, Google Colab, and VS Code**.

## Installation

Standard installation for standard terminals (Windows/macOS/Linux):
```bash
pip install timedinput
```

**For Jupyter/Colab Support:**
To enable timeout functionality inside Jupyter environments, install the optional UI dependencies:
```bash
pip install timedinput[jupyter]
```
*(If you use `timedinput` in Jupyter without these dependencies, it will gracefully fall back to a standard, non-timing `input()` prompt to prevent crashes).*

## Usage
The `timedinput` function takes three optional arguments: `prompt`, `timeout`, and `default`.

```python
from timedinput import timedinput

# Prompt the user for input with a timeout of 10 seconds
user_input = timedinput("Enter something: ", timeout=10)

# Prompt the user for input with a timeout of 5 seconds and a default value
user_input = timedinput("Enter something: ", timeout=5, default="default")
```

If the user enters input within the specified timeout, the function returns the user's input as a string. If the user does not enter input within the specified timeout, the function returns the default value (if one was provided) or raises a `TimeoutOccurred` exception.

## Compatibility
- **Terminals:** Works perfectly on all standard terminals across Windows and Unix-like operating systems.
- **Interactive:** Fully compatible with JupyterLab, Classic Notebook, Google Colab, and VS Code Interactive windows.

## License
Released under the MIT License. See the LICENSE file for more information.