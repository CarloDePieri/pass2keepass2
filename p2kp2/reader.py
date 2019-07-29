import os
import subprocess
from typing import List, Dict, Tuple

PassEntryCls = "PassEntry"


class PassReader:
    """Read a pass db and construct an in-memory version of it."""

    entries: List[PassEntryCls]

    def __init__(self, path: str = None, password: str = None):
        """Constructor for PassReader

        :param path: optional password-store location.
            Default is '~/.password-store'.
        """
        cmd = "pass"
        if password is not None:
            cmd = 'PASSWORD_STORE_GPG_OPTS="--pinentry-mode=loopback --batch ' \
                  '--passphrase={}" '.format(password) + cmd
            self.password = password
        if path is not None:
            self.path = os.path.abspath(os.path.expanduser(path))
            cmd = "PASSWORD_STORE_DIR={} ".format(self.path) + cmd
        else:
            self.path = os.path.expanduser("~/.password-store")
        if path is not None or password is not None:
            cmd = "env " + cmd
        self.pass_cmd = cmd
        self.entries = []

    def get_pass_entries(self) -> List[str]:
        """Return the list of entries in the pass db."""
        entries = [os.path.join(dirpath, fn)[len(self.path):-4]
                for dirpath, dirnames, files in os.walk(self.path)
                for fn in files if fn.endswith('.gpg')]
        return entries

    def parse_pass_entry(self, entry: str) -> PassEntryCls:
        """Return a parsed PassEntry."""
        return PassEntry(reader=self, entry=entry)

    def parse_db(self):
        """Populate the entries list with all the data from the pass db."""
        for entry in self.get_pass_entries():
            self.entries.append(self.parse_pass_entry(entry))


class PassEntry:
    """A simple pass entry in-memory representation"""

    to_skip: List[str] = ["---", ""]  # these lines will be skipped when parsing

    groups: List[str]
    title: str
    password: str
    url: str
    user: str
    notes: str
    custom_properties: Dict[str, str]

    def __init__(self, reader: PassReader, entry: str):
        """Constructor for PassEntry.

        :param reader:  a PassReader instance, used to access the entry
        :param entry:  string representing the entry name
        """
        self.url = ""
        self.user = ""
        self.notes = ""
        self.custom_properties = {}
        self.groups = self.get_groups(entry)
        self.title = self.get_title(entry)
        entry_string = self.decrypt_entry(reader, entry)
        self.parse_entry_string(entry_string)

    @staticmethod
    def get_title(entry: str) -> str:
        """Return the entry title."""
        return entry.split("/").pop()

    @staticmethod
    def get_groups(entry: str) -> List[str]:
        """Return the entry groups."""
        groups = entry.split("/")
        groups.pop()
        groups.pop(0)
        return groups

    @staticmethod
    def decrypt_entry(reader: PassReader, entry: str) -> str:
        """Decrypt the entry using pass and return it as a string."""
        cmd = subprocess.run(["bash", "-c", reader.pass_cmd + " show {}".format(entry)], capture_output=True)
        return cmd.stdout.decode()

    @staticmethod
    def is_valid_line(entry_line: str) -> bool:
        """Accept as valid only lines in the format of 'key: value'."""
        return entry_line.find(":") > 0

    @staticmethod
    def parse_entry_line(entry_line: str) -> Tuple[str, str]:
        """Parse a line in the format 'key: value'."""
        data = entry_line.split(":", 1)
        return data[0].strip(), data[1].strip()

    def parse_entry_string(self, entry_string: str) -> None:
        """Parse a entry and extract all useful data."""
        lines = entry_string.split("\n")
        self.password = lines.pop(0)

        lines = list(filter(lambda x: x not in self.to_skip and self.is_valid_line(x), lines))
        data = list(map(lambda x: self.parse_entry_line(x), lines))
        for key, value in data:
            if key == "url":
                self.url = value
            elif key == "user":
                self.user = value
            elif key == "notes":
                self.notes = value
            else:
                self.custom_properties.update({key: value})
