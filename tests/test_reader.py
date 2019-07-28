import os

import pytest

from p2kp2 import PassReader, PassKey


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
