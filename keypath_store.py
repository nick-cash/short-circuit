import os.path
import sys

__all__ = ['KeypathStore']

class KeypathStore(object):
    """A KeypathStore manages key->value data where the key is a keypath string and the value is anything.
       A keypath string is a string such that a.b.c represents 3 'levels' of data. This concept of keypath is somewhat
       inspired by Cocoa's Key-Value coding paradigm."""

    def __init__(self, data = None):
        """Data is a well-formated dict of keypath->value data to pre-populate this store."""
        if not isinstance(data, dict):
            data = {}
        self._data = data

    def dict_for_key(self, key, append_structure=True):
        data = self._data
        for token in key:
            if token in data:
                data = data[token]
            elif append_structure:
                data[token] = {}
                data = data[token]
            else:
                return None
        return data

    def set_value(self, keypath, value):
        """Associate keypath with value"""
        if not self._valid_key(keypath):
            return
        key = self._parse_keypath(keypath)
        data = self.dict_for_key(key[:-1])
        data[key[-1]] = value

    def get_value(self, keypath = ''):
        """Return the value associated with the keypath.
            A keypath of None returns None.
            A keypath of '' returns the entire data dict.
            Any other keypath returns the associated value in the data dict."""
        if not self._valid_key(keypath):
            return None
        elif keypath is '':
            return self._data
        key = self._parse_keypath(keypath)
        data = self.dict_for_key(key[:-1], False)
        if data is None:
            return None
        token = key[-1]
        if token in data:
            return data[token]
        return None

    def _valid_key(self, key):
        return isinstance(key, (str, unicode))

    def _parse_keypath(self, keypath):
        return keypath.split('.')
