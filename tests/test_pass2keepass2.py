import pytest

from pykeepass import PyKeePass


class TestInitialDb():
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
