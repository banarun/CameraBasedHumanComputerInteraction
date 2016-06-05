import sys

if sys.platform == 'win32':
    from .windows import PyKeyboard, PyKeyboardEvent
else:
    from .x11 import PyKeyboard, PyKeyboardEvent
