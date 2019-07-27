import os

import pytest

from pykeepass import PyKeePass
from pass2keepass2 import PassReader, PassKey


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
        assert len(self.kp.groups) == 0

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


class TestPassReaderGetKeys:
    """Test: PassReaderGetKeys..."""

    pr: PassReader

    @pytest.fixture(scope="class", autouse=True)
    def setup(self, request):
        """TestPassReaderGetKeys setup"""
        request.cls.pr = PassReader(path="tests/password-store")

    def test_should_return_the_list_of_pass_db_keys(self):
        """Pass reader get keys should return the list of pass db keys."""
        keys = self.pr.get_keys()
        assert "/test1" in keys
        assert "/web/test2" in keys
        assert "/docs/test3" in keys
        assert "/web/emails/test4" in keys


@pytest.mark.runthis
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

