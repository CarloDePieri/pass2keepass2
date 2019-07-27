import os

import pytest

from pykeepass import PyKeePass
from pykeepass.entry import Entry
from pykeepass.group import Group
from pass2keepass2 import PassReader, PassKey, P2KP2, DbAlreadyExistsException


class TestInitialDb:
    """Test: initial db..."""

    kb: PyKeePass

    @pytest.fixture(scope="class", autouse=True)
    def setup(self, request):
        """Test setup"""
        request.cls.kp: PyKeePass = PyKeePass("empty.kdbx")

    def test_should_be_empty(self):
        """Initial db should be empty."""
        assert len(self.kp.entries) == 0
        assert len(self.kp.groups) == 1
        assert self.kp.groups[0].is_root_group

    def test_should_have_no_password(self):
        """Initial db should have no password."""
        assert self.kp.password is None


class TestPassReaderInit:
    """Test: PassReaderInit..."""

    def test_should_have_sane_defaults(self):
        """Pass reader init should have sane defaults."""
        pr = PassReader()
        assert pr.pass_cmd == ["pass"]
        assert pr.path == os.path.expanduser("~/.password-store")

    def test_should_support_a_custom_password_store_path(self):
        """Pass reader init should support a custom password-store path."""
        custom_path = "~/some-other-folder"
        pr = PassReader(path=custom_path)
        assert pr.pass_cmd == ["env", "PASSWORD_STORE_DIR={}".format(os.path.expanduser(custom_path)), "pass"]
        assert pr.path == os.path.expanduser(custom_path)


class TestPassReader:
    """Test: PassReader..."""

    pr: PassReader

    @pytest.fixture(scope="class", autouse=True)
    def setup(self, request):
        """TestPassReader setup"""
        request.cls.pr = PassReader(path="tests/password-store")

    def test_get_keys_should_return_the_list_of_pass_db_keys(self):
        """Pass reader get keys should return the list of pass db keys."""
        keys = self.pr.get_keys()
        assert "/test1" in keys
        assert "/web/test2" in keys
        assert "/docs/test3" in keys
        assert "/web/emails/test4" in keys

    def test_parse_key_should_return_a_pass_key_object(self):
        """Pass reader parse key should return a PassKey object."""
        key = self.pr.parse_key("/test1")
        assert type(key) is PassKey
        assert key.title == "test1"

    def test_should_be_able_to_parse_the_db_with_parse_db(self):
        """Pass reader should be able to parse the db with parse db."""
        self.pr.parse_db()
        keys = self.pr.keys
        keys_names = list(map(lambda x: x.title, keys))
        assert len(keys) == 4
        assert "test1" in keys_names
        assert "test2" in keys_names
        assert "test3" in keys_names
        assert "test4" in keys_names


class TestPassKey:
    """Test: PassKey..."""

    pr: PassReader

    @pytest.fixture(scope="class", autouse=True)
    def setup(self, request):
        """TestPassKey setup"""
        request.cls.pr = PassReader(path="tests/password-store")

    def test_should_correctly_parse_the_group(self):
        """Pass key should correctly parse the group."""
        assert PassKey(self.pr, "/test1").groups == []
        assert PassKey(self.pr, "/docs/test3").groups == ["docs"]
        assert PassKey(self.pr, "/web/emails/test4").groups == ["web", "emails"]

    def test_should_correctly_parse_the_key_name(self):
        """Pass key should correctly parse the key name."""
        assert PassKey(self.pr, "/test1").title == "test1"
        assert PassKey(self.pr, "/docs/test3").title == "test3"
        assert PassKey(self.pr, "/web/emails/test4").title == "test4"

    def test_should_be_able_to_decrypt_a_key(self):
        """Pass key should be able to decrypt a key."""
        decrypted_key = PassKey.decrypt_key(self.pr, "/test1")
        key = 'somepassword\n---\nurl: someurl.com\nuser: myusername\nnotes: some notes something ' \
              'interesting\ncell_number: 00000000\n'
        assert decrypted_key == key

    def test_should_be_able_to_recognize_a_valid_key_line(self):
        """Pass key should be able to recognize a valid key line."""
        assert PassKey.is_valid_line("some: valid line") is True
        assert PassKey.is_valid_line("some NOT valid line") is False

    def test_should_be_able_to_parse_a_valid_key_line(self):
        """Pass key should be able to parse a valid key line."""
        assert PassKey.parse_key_line("some: valid line") == ("some", "valid line")

    def test_should_correctly_parse_all_relevant_data(self):
        """Pass key should correctly parse all relevant data."""
        key = PassKey(self.pr, "/test1")
        assert key.password == "somepassword"
        assert key.url == "someurl.com"
        assert key.user == "myusername"
        assert key.notes == "some notes something interesting"
        assert key.custom_properties["cell_number"] == "00000000"


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


@pytest.mark.runthis
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
        assert self.pass_entry0.title == self.entry0.title
        assert self.pass_entry1.title == self.entry1.title

    def test_should_correctly_set_the_password(self):
        """P2kp2 add_key should correctly set the password."""
        assert self.pass_entry0.password == self.entry0.password
        assert self.pass_entry1.password == self.entry1.password

    def test_should_correctly_set_the_username(self):
        """P2kp2 add_key should correctly set the username."""
        assert self.pass_entry0.user == self.entry0.username
        assert self.pass_entry1.user == self.entry1.username

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
