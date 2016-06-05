import time
from threading import Thread


class PyKeyboardMeta(object):

    def press_key(self, character=''):
        raise NotImplementedError

    def release_key(self, character=''):
        raise NotImplementedError

    def tap_key(self, character='', n=1, interval=0):
        """Press and release a given character key n times."""
        for i in range(n):
            self.press_key(character)
            self.release_key(character)
            time.sleep(interval)

    def special_key_assignment(self):
        raise NotImplementedError

    def lookup_character_value(self, character):
        raise NotImplementedError

    def is_char_shifted(self, character):
        """Returns True if the key character is uppercase or shifted."""
        if character.isupper():
            return True
        if character in '<>?:"{}|~!@#$%^&*()_+':
            return True
        return False

class PyKeyboardEventMeta:
    pass