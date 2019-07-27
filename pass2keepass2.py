# TODO warning about lack of in-memory security

import os
import subprocess
from typing import List


class PassReader:
    """Read a pass db and construct an in-memory version of it."""

    def __init__(self, path: str = None):
        """Constructor for PassReader

        :param path: optional password-store location.
            Default is '~/.password-store'.
        """
        if path is not None:
            self.path = os.path.abspath(os.path.expanduser(path))
            self.pass_cmd = ["env", "PASSWORD_STORE_DIR={}".format(self.path), "pass"]
        else:
            self.path = os.path.expanduser("~/.password-store")
            self.pass_cmd = ["pass"]

    def get_keys(self) -> List[str]:
        """Return the list of keys in the pass db."""
        keys = [os.path.join(dirpath, fn)[len(self.path):-4]
                for dirpath, dirnames, files in os.walk(self.path)
                for fn in files if fn.endswith('.gpg')]
        return keys


class PassKey:
    """A simple pass key representation"""

    groups: str
    title: str

    def __init__(self, reader: PassReader, key: str):
        """Constructor for PassKey.

        :param reader:  a PassReader instance, used to access the key
        :param key:  string representing the key name
        """
        self.groups = self.get_groups(key)
        self.title = self.get_title(key)
        key_string = self.decrypt_key(reader, key)

    @staticmethod
    def get_title(key: str) -> str:
        """Return the key title."""
        return key.split("/").pop()

    @staticmethod
    def get_groups(key: str) -> List[str]:
        """Return the key groups."""
        groups = key.split("/")
        groups.pop()
        groups.pop(0)
        return groups

    @staticmethod
    def decrypt_key(reader: PassReader, key: str) -> str:
        """Decrypt the key using pass and return it as a string."""
        return subprocess.check_output(reader.pass_cmd + ["show", key]).decode("UTF-8")
