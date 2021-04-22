import os
import sys
import pytest

from p2kp2.pass2keepass2 import main_func, import_custom_mapper, CustomMapperImportException
from p2kp2.reader import PassEntry, PassReader

from tests.conftest import test_db_file


class TestMainFunc:
    """Test: main_func..."""

    def test_should_call_quick_mode_when_instructed(self, monkeypatch, mocker):
        """Main func should call quick mode when instructed."""
        monkeypatch.setattr(sys, 'argv', ["pass2keepass2", "-q"])
        mocked_normal_mode = mocker.patch("p2kp2.pass2keepass2.exec_normal_mode")
        mocked_quick_mode = mocker.patch("p2kp2.pass2keepass2.exec_quick_mode")
        main_func()
        named_args = mocked_quick_mode.call_args[0][0]
        assert "quick" in named_args
        assert named_args.quick is True
        assert mocked_normal_mode.call_count == 0

    def test_should_not_go_in_quick_mode_by_default(self, monkeypatch, mocker):
        """Main func should not go in quick mode by default."""
        monkeypatch.setattr(sys, 'argv', ["pass2keepass2"])
        mocked_quick_mode = mocker.patch("p2kp2.pass2keepass2.exec_quick_mode")
        mocked_normal_mode = mocker.patch("p2kp2.pass2keepass2.exec_normal_mode")
        main_func()
        named_args = mocked_normal_mode.call_args[0][0]
        assert "quick" in named_args
        assert named_args.quick is False
        assert mocked_quick_mode.call_count == 0

    def test_should_accept_a_custom_function_and_pass_it_to_the_execs(self, monkeypatch, mocker):
        """... it should accept a custom function and pass it to the execs"""
        monkeypatch.setattr(sys, 'argv', ["pass2keepass2", "-c", "mycustomfunction.py"])
        mocked_normal_mode = mocker.patch("p2kp2.pass2keepass2.exec_normal_mode")
        main_func()
        named_args = mocked_normal_mode.call_args[0][0]
        assert "custom" in named_args
        assert named_args.custom == "mycustomfunction.py"

    def test_should_pass_the_provided_custom_function_to_the_passreader_in_normal_mode(self, monkeypatch, mocker):
        """... it should pass the provided custom function to the PassReader in normal mode"""
        # Mock the command line
        monkeypatch.setattr(sys, 'argv', ["pass2keepass2", "-c", "tests/custom_mapper.py",
                                          "-i", "tests/password-store",
                                          "-o", test_db_file])

        # Mock user input
        monkeypatch.setattr('builtins.input', lambda _: "y")
        passwords_iter = iter(["strong", "strong"])
        monkeypatch.setattr('p2kp2.pass2keepass2.getpass', lambda _: next(passwords_iter))

        # Mock db reader, keepass writer
        mocked_passreader = mocker.patch('p2kp2.pass2keepass2.PassReader')
        mocker.patch('p2kp2.pass2keepass2.P2KP2')

        # Mock the mapper importer and the passed mapper
        def mock_mapper(x):
            return x
        mocked_importer = mocker.patch(
            'p2kp2.pass2keepass2.import_custom_mapper', return_value=mock_mapper)

        main_func()

        # Check that the mapper importer was called correctly
        mocked_importer.assert_called_with(os.path.abspath("tests/custom_mapper.py"))

        # Check that the passreader was called with the right arguments
        mocked_passreader.assert_called_with(path='tests/password-store', mapper=mock_mapper)

    def test_should_pass_the_provided_custom_function_to_the_passreader_in_quick_mode(self, monkeypatch, mocker):
        """... it should pass the provided custom function to the PassReader in quick mode"""
        # Mock the command line
        monkeypatch.setattr(sys, 'argv', ["pass2keepass2", "-q", "-c", "tests/custom_mapper.py",
                                          "-i", "tests/password-store",
                                          "-o", test_db_file])

        # Mock user input
        monkeypatch.setattr('p2kp2.pass2keepass2.getpass', lambda _: "strong")

        # Mock db reader and keepass writer
        mocked_passreader = mocker.patch('p2kp2.pass2keepass2.PassReader')
        mocker.patch('p2kp2.pass2keepass2.P2KP2')

        # Mock the mapper importer and the passed mapper
        def mock_mapper(x):
            return x
        mocked_importer = mocker.patch(
            'p2kp2.pass2keepass2.import_custom_mapper', return_value=mock_mapper)

        main_func()

        # Check that the mapper importer was called correctly
        mocked_importer.assert_called_with(os.path.abspath("tests/custom_mapper.py"))

        # Check that the passreader was called with the right arguments
        mocked_passreader.assert_called_with(
            path='tests/password-store', mapper=mock_mapper, password="strong")


class TestTheCustomMapperImporter:
    """The custom mapper importer..."""

    def test_should_return_the_function_imported_from_the_provided_file(self):
        """... it should return the function imported from the provided file"""
        pr = PassReader(path="tests/password-store")
        entry = PassEntry(pr, "test1")
        mapper = import_custom_mapper("tests/custom_mapper.py")
        assert callable(mapper)
        assert mapper(entry).title == "test1_modified"

    def test_should_raise_an_exception_when_it_encounters_an_error(self):
        """... it should raise an exception when it encounters an error"""
        pr = PassReader(path="tests/password-store")
        entry = PassEntry(pr, "test1")
        with pytest.raises(CustomMapperImportException):
            import_custom_mapper("tests/custom_mapper_invalid.py")
