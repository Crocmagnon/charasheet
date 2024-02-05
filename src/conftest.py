import pytest
from django.core.management import call_command
from selenium.webdriver.remote.webdriver import WebDriver


@pytest.fixture(scope="session", autouse=True)
def _collectstatic():
    call_command("collectstatic", "--clear", "--noinput", "--verbosity=0")


@pytest.fixture()
def live_server(settings, live_server):
    settings.STORAGES = {
        "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
        "staticfiles": {
            "BACKEND": "whitenoise.storage.CompressedStaticFilesStorage",
        },
    }
    return live_server


@pytest.fixture()
def firefox_options(firefox_options):
    firefox_options.add_argument("-headless")
    return firefox_options


@pytest.fixture()
def selenium(selenium: WebDriver) -> WebDriver:
    selenium.implicitly_wait(3)
    selenium.set_window_size(3860, 2140)
    return selenium


@pytest.fixture(autouse=True)
def settings(settings):
    settings.DEBUG_TOOLBAR = False
    return settings


@pytest.fixture()
def initial_data() -> None:  # noqa: PT004
    call_command("loaddata", "initial_data")
