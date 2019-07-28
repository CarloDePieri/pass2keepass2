import os
import pkg_resources
from shutil import copyfile

from pykeepass import PyKeePass
from pykeepass.entry import Entry

from p2kp2 import PassReader, PassKey

empty_db_path = pkg_resources.resource_filename(__name__, "empty.kdbx")


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
            copyfile(empty_db_path, destination)
        else:
            raise DbAlreadyExistsException()
        self.db = PyKeePass(destination)
        self.db.password = password
        self.db.save()

    def populate_db(self, pass_reader: PassReader):
        """Populate the keepass db with data from the PassReader."""
        for pass_entry in pass_reader.keys:
            self.add_key(pass_entry)
        self.db.save()

    def add_key(self, key: PassKey) -> Entry:
        """Add a keepass entry to the db containing all data from the relative pass entry. Create the group if needed.

        :param key: the original pass entry
        :return: the newly added keepass entry
        """
        # find the correct group for the key. If not there, create it
        key_group = self.db.root_group  # start from the root group
        if len(key.groups) > 0:
            for group_name in key.groups:
                # since pass folder names are unique, the possible first result is also the only one
                group = self.db.find_groups(name=group_name, recursive=False, group=key_group, first=True)
                if group is None:
                    # the group is not already there, let's create it
                    group = self.db.add_group(destination_group=key_group, group_name=group_name)
                key_group = group
        # create the entry, setting group, title, user and pass
        entry = self.db.add_entry(key_group, key.title, key.user, key.password)
        # set the url and the notes
        entry.url = key.url
        entry.notes = key.notes
        # add all custom fields
        for key, value in key.custom_properties.items():
            entry.set_custom_property(key, value)
        return entry
