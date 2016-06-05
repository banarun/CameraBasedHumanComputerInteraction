from Xlib.display import Display
from Xlib import X
from Xlib.ext.xtest import fake_input
from Xlib.ext import record
from Xlib.protocol import rq
import Xlib.XK

from .base import PyKeyboardMeta, PyKeyboardEventMeta

import time
import string

special_X_keysyms = {
    ' ': "space",
    '\t': "Tab",
    '\n': "Return",
    '\r': "Return",
    '\e': "Escape",
    '!': "exclam",
    '#': "numbersign",
    '%': "percent",
    '$': "dollar",
    '&': "ampersand",
    '"': "quotedbl",
    '\'': "apostrophe",
    '(': "parenleft",
    ')': "parenright",
    '*': "asterisk",
    '=': "equal",
    '+': "plus",
    ',': "comma",
    '-': "minus",
    '.': "period",
    '/': "slash",
    ':': "colon",
    ';': "semicolon",
    '<': "less",
    '>': "greater",
    '?': "question",
    '@': "at",
    '[': "bracketleft",
    ']': "bracketright",
    '\\': "backslash",
    '^': "asciicircum",
    '_': "underscore",
    '`': "grave",
    '{': "braceleft",
    '|': "bar",
    '}': "braceright",
    '~': "asciitilde"
    }

class PyKeyboard(PyKeyboardMeta):

    def __init__(self, display=None):
        PyKeyboardMeta.__init__(self)
        self.display = Display(display)
        self.display2 = Display(display)
        self.special_key_assignment()

    def press_key(self, character=''):

        try:  # Detect uppercase or shifted character
            shifted = self.is_char_shifted(character)
        except AttributeError:  # Handle the case of integer keycode argument
            fake_input(self.display, X.KeyPress, character)
            self.display.sync()
        else:
            if shifted:
                fake_input(self.display, X.KeyPress, self.shift_key)
            keycode = self.lookup_character_keycode(character)
            fake_input(self.display, X.KeyPress, keycode)
            self.display.sync()

    def release_key(self, character=''):
        """
        Release a given character key. Also works with character keycodes as
        integers, but not keysyms.
        """
        try:  # Detect uppercase or shifted character
            shifted = self.is_char_shifted(character)
        except AttributeError:  # Handle the case of integer keycode argument
            fake_input(self.display, X.KeyRelease, character)
            self.display.sync()
        else:
            if shifted:
                fake_input(self.display, X.KeyRelease, self.shift_key)
            keycode = self.lookup_character_keycode(character)
            fake_input(self.display, X.KeyRelease, keycode)
            self.display.sync()

    def special_key_assignment(self):

        self.backspace_key = self.lookup_character_keycode('BackSpace')
        self.tab_key = self.lookup_character_keycode('Tab')
        self.linefeed_key = self.lookup_character_keycode('Linefeed')
        self.clear_key = self.lookup_character_keycode('Clear')
        self.return_key = self.lookup_character_keycode('Return')
        self.enter_key = self.return_key  # Because many keyboards call it "Enter"
        self.pause_key = self.lookup_character_keycode('Pause')
        self.scroll_lock_key = self.lookup_character_keycode('Scroll_Lock')
        self.sys_req_key = self.lookup_character_keycode('Sys_Req')
        self.escape_key = self.lookup_character_keycode('Escape')
        self.delete_key = self.lookup_character_keycode('Delete')
        #Modifier Keys
        self.shift_l_key = self.lookup_character_keycode('Shift_L')
        self.shift_r_key = self.lookup_character_keycode('Shift_R')
        self.shift_key = self.shift_l_key  # Default Shift is left Shift
        self.alt_l_key = self.lookup_character_keycode('Alt_L')
        self.alt_r_key = self.lookup_character_keycode('Alt_R')
        self.alt_key = self.alt_l_key  # Default Alt is left Alt
        self.control_l_key = self.lookup_character_keycode('Control_L')
        self.control_r_key = self.lookup_character_keycode('Control_R')
        self.control_key = self.control_l_key  # Default Ctrl is left Ctrl
        self.caps_lock_key = self.lookup_character_keycode('Caps_Lock')
        self.capital_key = self.caps_lock_key  # Some may know it as Capital
        self.shift_lock_key = self.lookup_character_keycode('Shift_Lock')
        self.meta_l_key = self.lookup_character_keycode('Meta_L')
        self.meta_r_key = self.lookup_character_keycode('Meta_R')
        self.super_l_key = self.lookup_character_keycode('Super_L')
        self.windows_l_key = self.super_l_key  # Cross-support; also it's printed there
        self.super_r_key = self.lookup_character_keycode('Super_R')
        self.windows_r_key = self.super_r_key  # Cross-support; also it's printed there
        self.hyper_l_key = self.lookup_character_keycode('Hyper_L')
        self.hyper_r_key = self.lookup_character_keycode('Hyper_R')
        #Cursor Control and Motion
        self.home_key = self.lookup_character_keycode('Home')
        self.up_key = self.lookup_character_keycode('Up')
        self.down_key = self.lookup_character_keycode('Down')
        self.left_key = self.lookup_character_keycode('Left')
        self.right_key = self.lookup_character_keycode('Right')
        self.end_key = self.lookup_character_keycode('End')
        self.begin_key = self.lookup_character_keycode('Begin')
        self.page_up_key = self.lookup_character_keycode('Page_Up')
        self.page_down_key = self.lookup_character_keycode('Page_Down')
        self.prior_key = self.lookup_character_keycode('Prior')
        self.next_key = self.lookup_character_keycode('Next')
        #Misc Functions
        self.select_key = self.lookup_character_keycode('Select')
        self.print_key = self.lookup_character_keycode('Print')
        self.print_screen_key = self.print_key  # Seems to be the same thing
        self.snapshot_key = self.print_key  # Another name for printscreen
        self.execute_key = self.lookup_character_keycode('Execute')
        self.insert_key = self.lookup_character_keycode('Insert')
        self.undo_key = self.lookup_character_keycode('Undo')
        self.redo_key = self.lookup_character_keycode('Redo')
        self.menu_key = self.lookup_character_keycode('Menu')
        self.apps_key = self.menu_key  # Windows...
        self.find_key = self.lookup_character_keycode('Find')
        self.cancel_key = self.lookup_character_keycode('Cancel')
        self.help_key = self.lookup_character_keycode('Help')
        self.break_key = self.lookup_character_keycode('Break')
        self.mode_switch_key = self.lookup_character_keycode('Mode_switch')
        self.script_switch_key = self.lookup_character_keycode('script_switch')
        self.num_lock_key = self.lookup_character_keycode('Num_Lock')
        #Keypad Keys: Dictionary structure
        keypad = ['Space', 'Tab', 'Enter', 'F1', 'F2', 'F3', 'F4', 'Home',
                  'Left', 'Up', 'Right', 'Down', 'Prior', 'Page_Up', 'Next',
                  'Page_Down', 'End', 'Begin', 'Insert', 'Delete', 'Equal',
                  'Multiply', 'Add', 'Separator', 'Subtract', 'Decimal',
                  'Divide', 0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
        self.keypad_keys = {k: self.lookup_character_keycode('KP_'+str(k)) for k in keypad}
        self.numpad_keys = self.keypad_keys
        #Function Keys/ Auxilliary Keys
        #FKeys
        self.function_keys = [None] + [self.lookup_character_keycode('F'+str(i)) for i in range(1,36)]
        #LKeys
        self.l_keys = [None] + [self.lookup_character_keycode('L'+str(i)) for i in range(1,11)]
        #RKeys
        self.r_keys = [None] + [self.lookup_character_keycode('R'+str(i)) for i in range(1,16)]

        #Unsupported keys from windows
        self.kana_key = None
        self.hangeul_key = None # old name - should be here for compatibility
        self.hangul_key = None
        self.junjua_key = None
        self.final_key = None
        self.hanja_key = None
        self.kanji_key = None
        self.convert_key = None
        self.nonconvert_key = None
        self.accept_key = None
        self.modechange_key = None
        self.sleep_key = None

    def lookup_character_keycode(self, character):
        keysym = Xlib.XK.string_to_keysym(character)
        if keysym == 0:
            keysym = Xlib.XK.string_to_keysym(special_X_keysyms[character])
        return self.display.keysym_to_keycode(keysym)


class PyKeyboardEvent(PyKeyboardEventMeta):
    pass