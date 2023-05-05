# timedinput 
A Python module that waits for a specified amount of time for user input. If no input is received within the given timeout period, the module sets the variable value as per the default or raises an exception. This module is similar to the [inputtimeout](https://pypi.org/project/inputimeout/) module, but with a few differences.

## Usage
The timedinput function takes three optional arguments: prompt, timeout, and default.
```py
from timedinput import timedinput

# Prompt the user for input with a timeout of 10 seconds
user_input = timedinput("Enter something: ", timeout=10)

# Prompt the user for input with a timeout of 5 seconds and a default value of "default"
user_input = timedinput("Enter something: ", timeout=5, default="default")
```
If the user enters input within the specified timeout, the function returns the user's input as a string. If the user does not enter input within the specified timeout, the function returns the default value (if one was provided) or raises a TimeoutOccurred exception.

## Installation
The `timedinput` module can be installed using pip.
```
pip install timedinput
```

## Compatibility
Works on all platforms, including Windows and Unix-like operating systems.

## License
Released under the MIT License. See the LICENSE file for more information.