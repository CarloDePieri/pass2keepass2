import os

import pytest

from p2kp2 import PassReader, PassEntry


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

    def test_get_pass_entries_should_return_the_list_of_pass_db_entries(self):
        """Pass reader get pass entries should return the list of pass db entries."""
        entries = self.pr.get_pass_entries()
        assert "/test1" in entries
        assert "/web/test2" in entries
        assert "/docs/test3" in entries
        assert "/web/emails/test4" in entries

    def test_parse_pass_entry_should_return_a_pass_entry_object(self):
        """Pass reader parse pass entry should return a PassEntry object."""
        entry = self.pr.parse_pass_entry("/test1")
        assert type(entry) is PassEntry
        assert entry.title == "test1"

    def test_should_be_able_to_parse_the_db_with_parse_db(self):
        """Pass reader should be able to parse the db with parse db."""
        self.pr.parse_db()
        entries = self.pr.entries
        entries_name = list(map(lambda x: x.title, entries))
        assert len(entries) == 4
        assert "test1" in entries_name
        assert "test2" in entries_name
        assert "test3" in entries_name
        assert "test4" in entries_name


class TestPassEntry:
    """Test: PassEntry..."""

    pr: PassReader

    @pytest.fixture(scope="class", autouse=True)
    def setup(self, request):
        """TestPassEntry setup"""
        request.cls.pr = PassReader(path="tests/password-store")

    def test_should_correctly_parse_the_group(self):
        """Pass entry should correctly parse the group."""
        assert PassEntry(self.pr, "/test1").groups == []
        assert PassEntry(self.pr, "/docs/test3").groups == ["docs"]
        assert PassEntry(self.pr, "/web/emails/test4").groups == ["web", "emails"]

    def test_should_correctly_parse_the_entry_name(self):
        """Pass entry should correctly parse the entry name."""
        assert PassEntry(self.pr, "/test1").title == "test1"
        assert PassEntry(self.pr, "/docs/test3").title == "test3"
        assert PassEntry(self.pr, "/web/emails/test4").title == "test4"

    def test_should_be_able_to_decrypt_an_entry(self):
        """Pass entry should be able to decrypt an entry."""
        decrypted_entry = PassEntry.decrypt_entry(self.pr, "/test1")
        entry = 'somepassword\n---\nurl: someurl.com\nuser: myusername\nnotes: some notes something ' \
              'interesting\ncell_number: 00000000\n'
        assert decrypted_entry == entry

    def test_should_be_able_to_recognize_a_valid_entry_line(self):
        """Pass entry should be able to recognize a valid entry line."""
        assert PassEntry.is_valid_line("some: valid line") is True
        assert PassEntry.is_valid_line("some NOT valid line") is False

    def test_should_be_able_to_parse_a_valid_entry_line(self):
        """Pass entry should be able to parse a valid entry line."""
        assert PassEntry.parse_entry_line("some: valid line") == ("some", "valid line")

    def test_should_correctly_parse_all_relevant_data(self):
        """Pass entry should correctly parse all relevant data."""
        entry = PassEntry(self.pr, "/test1")
        assert entry.password == "somepassword"
        assert entry.url == "someurl.com"
        assert entry.user == "myusername"
        assert entry.notes == "some notes something interesting"
        assert entry.custom_properties["cell_number"] == "00000000"
