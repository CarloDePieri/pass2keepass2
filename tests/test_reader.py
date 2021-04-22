import os

import pytest

from p2kp2 import PassReader, PassEntry, CustomMapperExecException


class TestPassReaderInit:
    """Test: PassReaderInit..."""

    def test_should_have_sane_defaults(self):
        """Pass reader init should have sane defaults."""
        pr = PassReader()
        assert pr.path == os.path.expanduser("~/.password-store")

    def test_should_support_a_custom_password_store_path(self):
        """Pass reader init should support a custom password-store path."""
        custom_path = "~/some-other-folder"
        pr = PassReader(path=custom_path)
        assert pr.path == os.path.expanduser(custom_path)

    def test_should_expose_the_password(self):
        """Pass reader init should expose the password."""
        password = "somepass"
        pr = PassReader(password=password)
        assert pr.password == password

    def test_should_set_a_none_custom_mapper_by_default(self):
        """... it should set a None custom mapper by default"""
        pr = PassReader(path="tests/password-store")
        assert pr.mapper is None

    def test_should_have_mapper_pointing_to_a_function_when_custom_is_provided(self):
        """... it should have mapper pointing to a function when custom is provided"""
        def custom_mapper():
            pass
        pr = PassReader(path="tests/password-store", mapper=custom_mapper)
        assert pr.mapper is custom_mapper


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
        assert "test1" in entries
        assert "web/test2" in entries
        assert "docs/test3" in entries
        assert "web/emails/test4" in entries

    def test_parse_pass_entry_should_return_a_pass_entry_object(self):
        """Pass reader parse pass entry should return a PassEntry object."""
        entry = self.pr.parse_pass_entry("test1")
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

    def test_should_apply_the_mapper_when_provided(self):
        """... it should apply the mapper when provided"""
        def custom_mapper(entry: PassEntry) -> PassEntry:
            entry.title += "_modified"
            if 'cell_number' in entry.custom_properties:
                entry.custom_properties["cell_number"] = "11111111"
            return entry
        pr = PassReader(path="tests/password-store", mapper=custom_mapper)
        entry = pr.parse_pass_entry("test1")
        assert entry.title == "test1_modified"
        assert entry.custom_properties['cell_number'] == "11111111"

    def test_should_raise_an_exception_if_a_provided_custom_mapper_contains_errors(self):
        """... it should raise an exception if a provided custom mapper contains errors"""
        def custom_broken_mapper(_):
            raise Exception
        pr = PassReader(path="tests/password-store", mapper=custom_broken_mapper)
        with pytest.raises(CustomMapperExecException):
            pr.parse_pass_entry("test1")


class TestPassEntry:
    """Test: PassEntry..."""

    pr: PassReader

    @pytest.fixture(scope="class", autouse=True)
    def setup(self, request):
        """TestPassEntry setup"""
        request.cls.pr = PassReader(path="tests/password-store")

    def test_should_correctly_parse_the_group(self):
        """Pass entry should correctly parse the group."""
        assert PassEntry(self.pr, "test1").groups == []
        assert PassEntry(self.pr, "docs/test3").groups == ["docs"]
        assert PassEntry(self.pr, "web/emails/test4").groups == ["web", "emails"]

    def test_should_correctly_parse_the_entry_name(self):
        """Pass entry should correctly parse the entry name."""
        assert PassEntry(self.pr, "test1").title == "test1"
        assert PassEntry(self.pr, "docs/test3").title == "test3"
        assert PassEntry(self.pr, "web/emails/test4").title == "test4"

    def test_should_be_able_to_decrypt_an_entry(self):
        """Pass entry should be able to decrypt an entry."""
        decrypted_entry = PassEntry.decrypt_entry(self.pr, "test1")
        entry = 'somepassword\n---\nurl: someurl.com\nuser: myusername\nnotes: some notes something ' \
                'interesting\ncell_number: 00000000\n'
        assert decrypted_entry == entry

    def test_should_be_able_to_decrypt_an_entry_with_a_given_password(self):
        """Pass entry should be able to decrypt an entry with a given password."""
        pr = PassReader(path="tests/password-store-with-pass", password="pass2keepass2")
        decrypted_entry = PassEntry.decrypt_entry(pr, "test1")
        entry = 'F_Yq^5vgeyMCgYf-tW\\!T7Uj|\n---\nurl: someurl.com\n'
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
        entry = PassEntry(self.pr, "test1")
        assert entry.password == "somepassword"
        assert entry.url == "someurl.com"
        assert entry.user == "myusername"
        assert entry.notes == "some notes something interesting"
        assert entry.custom_properties["cell_number"] == "00000000"
