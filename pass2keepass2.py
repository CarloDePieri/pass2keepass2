import os


class PassReader:
    """Read a pass db and construct an in-memory version of it."""

    def __init__(self, path=None):
        """Constructor for PassReader

        :param path: optional password-store location.
            Default is '~/.password-store'.
        """
        if path is not None:
            self.path = os.path.abspath(os.path.expanduser(path))
            self.pass_cmd = ["env", "PASSWORD_STORE_DIR={}".format(self.path), "pass"]
        else:
            self.path = os.path.expanduser("~/.password-store")
            self.pass_cmd = ["pass"]



