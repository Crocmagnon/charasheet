import pytest
from django.core.management import call_command


@pytest.fixture(scope="session", autouse=True)
def collectstatic():
    call_command("collectstatic", "--clear", "--noinput", "--verbosity=0")


@pytest.fixture
def firefox_options(firefox_options):
    firefox_options.add_argument("-headless")
    return firefox_options


@pytest.fixture
def chrome_options(chrome_options):
    chrome_options.add_argument("--headless")
    return chrome_options


@pytest.fixture(autouse=True)
def settings(settings):
    settings.DEBUG_TOOLBAR = False
    return settings


@pytest.fixture
def initial_data(db: None) -> None:
    call_command("loaddata", "initial_data")
