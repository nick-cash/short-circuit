import json
from keypath_store import *

__all__ = ['KeyedConfigController']

class KeyedConfigController(object):
    def __init__(self, write_filepath, default_filepath = None):
        self.write_filepath = write_filepath
        self.default_store = self._read_store_from_file(default_filepath)
        self.write_store = self._read_store_from_file(write_filepath)

    def _read_store_from_file(self, filepath):
        data = {}
        if filepath is not None:
            try:
                handle = open(filepath, 'r')
            except IOError:
                """Well this whole bit is seven flavors of disturbing..."""
                handle = open(filepath, 'w')
                handle.write('')
                handle.close()
                handle = open(filepath, 'r')
            try:
                data = json.load(handle)
            except ValueError:
                pass
            handle.close()
        return KeypathStore(data)

    def _write_store_to_file(self, filepath, store):
        handle = open(filepath, 'w')
        json.dump(store.get_value(), handle, indent=2)
        handle.close()

    def set(self, key, value):
        default_value = self.default_store.get_value(key)
        if value == default_value:
            self.write_store.clear_value(key)
        else:
            self.write_store.set_value(key, value)
        self._write_store_to_file(self.write_filepath, self.write_store)

    def get(self, key = ''):
        write_value = self.write_store.get_value(key)
        if write_value is not None:
            return write_value
        default_value = self.default_store.get_value(key)
        return default_value
