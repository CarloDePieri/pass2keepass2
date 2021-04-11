import os
from typing import List, Dict, Tuple, Callable

from passpy import Store
from passpy.gpg import read_key
from rx.subject import Subject

PassEntryCls = "PassEntry"


class PassReader:
    """Read a pass db and construct an in-memory version of it."""

    entries: List[PassEntryCls]
    store: Store

    def __init__(self, path: str = None, password: str = None, mapper: Callable = None):
        """Constructor for PassReader

        :param path: optional password-store location.
            Default is '~/.password-store'.
        """
        if path is None:
            self.path = os.path.expanduser("~/.password-store")
        else:
            self.path = os.path.abspath(os.path.expanduser(path))
        self.store = Store(store_dir=self.path)
        self.entries = []
        self.password = password
        self.event_stream = Subject()
        self.mapper = mapper

    def get_pass_entries(self) -> List[str]:
        """Returns all store entries."""
        return self._get_entries_at_path()

    def _get_entries_at_path(self, path: str = "/") -> List[str]:
        """Recursive scan of a store path.

        :param path: the path to scan, default at root
        :return: a list of entries name
        """
        folders, entries = self.store.list_dir(self.path + path)
        if len(folders) > 0:
            for folder in folders:
                for entry in self._get_entries_at_path("/{}".format(folder)):
                    entries.append(entry)
        return entries

    def parse_pass_entry(self, entry_name: str) -> PassEntryCls:
        """Return a parsed PassEntry."""
        entry = PassEntry(reader=self, entry=entry_name)
        if self.mapper is not None:
            try:
                entry = self.mapper(entry)
            except:
                raise CustomMapperExecException()
        return entry

    def parse_db(self):
        """Populate the entries list with all the data from the pass db."""
        i = 0
        for entry in self.get_pass_entries():
            self.entries.append(self.parse_pass_entry(entry))
            i = i + 1
            self.event_stream.on_next(i)


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
        return groups

    @staticmethod
    def decrypt_entry(reader: PassReader, entry: str) -> str:
        """Decrypt the entry using pass and return it as a string."""
        if reader.password is None or reader.password == "":
            entry = reader.store.get_key(entry)
        else:
            # implement my own get_key and pass a custom gpg pass
            gpg_opts = reader.store.gpg_opts + \
                ["--pinentry-mode=loopback", f"--passphrase={reader.password}"]
            entry = read_key(reader.path + f"/{entry}.gpg", reader.store.gpg_bin, gpg_opts)
        return entry

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
            elif key == "user" or key == "login":
                self.user = value
            elif key == "notes":
                self.notes = value
            else:
                self.custom_properties.update({key: value})


class CustomMapperExecException(Exception):
    """Exception raised when encountering an error when executing an user provided mapper function."""
