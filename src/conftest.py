import pytest
from django.core.management import call_command


@pytest.fixture(scope="session", autouse=True)
def collectstatic():
    call_command("collectstatic", "--clear", "--noinput", "--verbosity=0")


@pytest.fixture
def firefox_options(firefox_options):
    firefox_options.add_argument("-headless")
    return firefox_options
