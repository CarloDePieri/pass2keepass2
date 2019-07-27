# TODO warning about lack of in-memory security

import os
import subprocess
from shutil import copyfile
from typing import List, Tuple, Dict

from pykeepass import PyKeePass
from pykeepass.entry import Entry

PassKeyCls = "PassKey"


class PassReader:
    """Read a pass db and construct an in-memory version of it."""

    keys: List[PassKeyCls] = []

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

    def parse_key(self, key: str) -> PassKeyCls:
        """Return a parsed PassKey."""
        return PassKey(reader=self, key=key)

    def parse_db(self):
        """Populate the keys list with all the data from the pass db."""
        for key in self.get_keys():
            self.keys.append(self.parse_key(key))


class PassKey:
    """A simple pass key in-memory representation"""

    groups: List[str] = []
    title: str = ""
    password: str = ""
    url: str = ""
    user: str = ""
    notes: str = ""
    custom_properties: Dict[str, str] = {}
    to_skip = ["---", ""]  # these lines will be skipped when parsing

    def __init__(self, reader: PassReader, key: str):
        """Constructor for PassKey.

        :param reader:  a PassReader instance, used to access the key
        :param key:  string representing the key name
        """
        self.groups = self.get_groups(key)
        self.title = self.get_title(key)
        key_string = self.decrypt_key(reader, key)
        self.parse_key_string(key_string)

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

    @staticmethod
    def is_valid_line(key_line: str) -> bool:
        """Accept as valid only lines in the format of 'key: value'."""
        return key_line.find(":") > 0

    @staticmethod
    def parse_key_line(key_line: str) -> Tuple[str, str]:
        """Parse a line in the format 'key: value'."""
        data = key_line.split(":", 1)
        return data[0].strip(), data[1].strip()

    def parse_key_string(self, key_string: str) -> None:
        """Parse a key and extract all useful data."""
        lines = key_string.split("\n")
        self.password = lines.pop(0)

        lines = list(filter(lambda x: x not in self.to_skip and self.is_valid_line(x), lines))
        data = list(map(lambda x: self.parse_key_line(x), lines))
        for key, value in data:
            if key == "url":
                self.url = value
            elif key == "user":
                self.user = value
            elif key == "notes":
                self.notes = value
            else:
                self.custom_properties.update({key: value})


class DbAlreadyExistsException(Exception):
    """Trying to overwrite an already existing keepass db."""


class P2KP2:
    """Convert a Pass db into a Keepass2 one."""

    db: PyKeePass

    def __init__(self, password: str, destination: str = "pass.kdbx"):
        """Constructor for P2KP2

        :param password: the password for the new Keepass db
        :param destination: the final db path
        """
        if not os.path.exists(destination):
            copyfile("empty.kdbx", destination)
        else:
            raise DbAlreadyExistsException()
        self.db = PyKeePass(destination)
        self.db.password = password
        self.db.save()

    def add_key(self, key: PassKey) -> Entry:
        group = self.db.root_group
        return self.db.add_entry(group, key.title, key.user, key.password)
