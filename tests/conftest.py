import os
import pytest


test_pass = "somesecurepassword"
test_db_file = "tests/test-db.kdbx"


def delete_test_db():
    if os.path.exists(test_db_file):
        os.remove(test_db_file)


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
