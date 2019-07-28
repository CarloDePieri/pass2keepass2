import os

import pkg_resources
import pytest
from pykeepass import PyKeePass
from pykeepass.entry import Entry
from pykeepass.group import Group

from p2kp2 import P2KP2, DbAlreadyExistsException, PassReader, PassKey, empty_db_path

test_pass = "somesecurepassword"
test_db = "tests/test-db.kdbx"


def delete_test_db():
    if os.path.exists(test_db):
        os.remove(test_db)


@pytest.fixture
def reset_db_every_test():
    """Delete the test db every test."""
    yield
    delete_test_db()


@pytest.fixture(scope="class")
def reset_db_after_all_class_test():
    """Delete the test db after all the class test run."""
    yield
    delete_test_db()


class TestInitialDb:
    """Test: initial db..."""

    kb: PyKeePass

    @pytest.fixture(scope="class", autouse=True)
    def setup(self, request):
        """Test setup"""
        request.cls.kp: PyKeePass = PyKeePass(empty_db_path)

    def test_should_be_empty(self):
        """Initial db should be empty."""
        assert len(self.kp.entries) == 0
        assert len(self.kp.groups) == 1
        assert self.kp.groups[0].is_root_group

    def test_should_have_no_password(self):
        """Initial db should have no password."""
        assert self.kp.password is None


@pytest.mark.usefixtures("reset_db_every_test")
class TestP2kp2Init:
    """Test: P2kp2 init..."""

    def test_should_create_a_default_new_file(self):
        """P2kp2 init should create a default new file."""
        P2KP2(password=test_pass)
        assert os.path.exists("pass.kdbx")
        os.remove("pass.kdbx")

    def test_should_allow_to_specify_a_custom_path_for_the_new_db_file(self):
        """P2kp2 init should allow to specify a custom path for the new db file."""
        P2KP2(password=test_pass, destination=test_db)

    def test_should_raise_an_error_if_the_db_already_exists(self):
        """P2kp2 init should raise an error if the db already exists."""
        open(test_db, "a").close()
        with pytest.raises(DbAlreadyExistsException):
            P2KP2(password=test_pass, destination=test_db)
            os.remove("tests/test-db.kdbx")

    def test_should_set_the_given_password(self):
        """P2kp2 should set the given password."""
        P2KP2(password=test_pass, destination=test_db)
        PyKeePass(test_db, password=test_pass)  # this will fail if the pass is wrong


class TestP2Kp2AddKey:
    """Test: P2kp2 add_key..."""

    reader: PassReader
    p2kp2: P2KP2
    entry0: Entry
    entry1: Entry
    pass_entry0: PassKey
    pass_entry1: PassKey

    @pytest.fixture(scope="class", autouse=True)
    def setup(self, request, reset_db_after_all_class_test):
        """TestP2Kp2AddKey setup"""
        reader = PassReader(path="tests/password-store")
        reader.parse_db()
        request.cls.reader = reader
        request.cls.p2kp2 = P2KP2(password=test_pass, destination=test_db)
        request.cls.pass_entry0 = list(filter(lambda x: x.title == "test1", self.reader.keys))[0]
        request.cls.pass_entry1 = list(filter(lambda x: x.title == "test4", self.reader.keys))[0]
        request.cls.entry0 = request.cls.p2kp2.add_key(request.cls.pass_entry0)
        request.cls.entry1 = request.cls.p2kp2.add_key(request.cls.pass_entry1)

    def test_should_correctly_set_the_title(self):
        """P2kp2 add_key should correctly set the title."""
        assert self.entry0.title == self.pass_entry0.title
        assert self.entry1.title == self.pass_entry1.title

    def test_should_correctly_set_the_password(self):
        """P2kp2 add_key should correctly set the password."""
        assert self.entry0.password == self.pass_entry0.password
        assert self.entry1.password == self.pass_entry1.password

    def test_should_correctly_set_the_username(self):
        """P2kp2 add_key should correctly set the username."""
        assert self.entry0.username == self.pass_entry0.user
        assert self.entry1.username == self.pass_entry1.user

    def test_should_return_a_pykeepass_entry(self):
        """P2kp2 add_key should return a pykeepass entry."""
        assert type(self.entry0) is Entry
        assert type(self.entry1) is Entry

    def test_should_actually_add_the_key(self):
        """P2kp2 add_key should actually add the key."""
        assert self.entry0 in self.p2kp2.db.entries
        assert self.entry1 in self.p2kp2.db.entries

    def test_should_correctly_set_groups(self):
        """P2kp2 add_key should correctly set groups."""
        group0: Group = self.entry0.group
        assert group0.path == "/"
        group1: Group = self.entry1.group
        assert group1.path == "web/emails"

    def test_should_be_able_to_add_entries_in_already_existing_groups(self):
        """P2kp2 add_key should be able to use existing groups."""
        ngroups = len(self.p2kp2.db.groups)
        pass_entry2 = list(filter(lambda x: x.title == "test2", self.reader.keys))[0]
        entry2 = self.p2kp2.add_key(pass_entry2)
        assert entry2.group.path == "web"
        assert ngroups == len(self.p2kp2.db.groups)

    def test_should_correctly_set_custom_properties(self):
        """P2kp2 add_key should correctly set custom properties."""
        for key, value in self.pass_entry0.custom_properties.items():
            assert self.entry0.get_custom_property(key) == value

    def test_should_correctly_set_the_url(self):
        """P2kp2 add_key should correctly set the url."""
        assert self.entry0.url == self.pass_entry0.url

    def test_should_correctly_set_the_notes(self):
        """P2kp2 add_key should correctly set the notes."""
        assert self.entry0.notes == self.pass_entry0.notes


class TestP2Kp2:
    """Test: P2kp2..."""

    db: PyKeePass
    pr: PassReader

    @pytest.fixture(scope="class", autouse=True)
    def setup(self, request, reset_db_after_all_class_test):
        """TestP2Kp2 setup"""
        # prepare the PassReader
        reader = PassReader(path="tests/password-store")
        reader.parse_db()
        request.cls.pr = reader
        # populate the new db
        p2kp2 = P2KP2(password=test_pass, destination=test_db)
        p2kp2.populate_db(reader)
        # prepare it to be read
        request.cls.db = PyKeePass(test_db, password=test_pass)

    def test_should_actually_populate_the_db_with_populate_db(self):
        """P 2 kp 2 should actually populate the db with populate db."""
        assert len(self.db.entries) == 4

