import sys

import pytest

from p2kp2.pass2keepass2 import main_func


@pytest.mark.runthis
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

