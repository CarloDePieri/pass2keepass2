from invoke import task


TEST_FOLDER = "tests"
PROJECT_FOLDER = "p2kp2"


@task
def clean_cache(c):
    print("Cleaning module cache.")
    c.run("rm -rf .pytest_cache")


@task
def clean_test_cache(c):
    print("Cleaning test cache.")
    c.run("rm -rf {}/.pytest_cache".format(TEST_FOLDER))


@task(pre=[clean_cache, clean_test_cache])
def clean(c):
    pass


@task
def test(c, s=False):
    capture = ""
    if s:
        capture = " -s"
    c.run("pipenv run pytest{} {}".format(capture, TEST_FOLDER), pty=True)


@task
def test_spec(c):
    c.run("pipenv run pytest --spec -p no:sugar {}".format(TEST_FOLDER), pty=True)


@task
def test_this(c, s=False):
    capture = ""
    if s:
        capture = " -s"
    c.run("pipenv run pytest{} -p no:sugar -m 'runthis' {}".format(capture, TEST_FOLDER), pty=True)


@task
def test_coverage(c, s=False):
    capture = ""
    if s:
        capture = " -s"
    c.run("pipenv run pytest --cov='{}'{} {}".format(PROJECT_FOLDER, capture, TEST_FOLDER), pty=True)
