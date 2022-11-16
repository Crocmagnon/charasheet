import pytest
from django.core.management import call_command
from django.urls import reverse
from model_bakery import baker
from pytest_django.live_server_helper import LiveServer
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.webdriver import WebDriver
from selenium.webdriver.support.select import Select

from character.models import Character
from character.tests.test_interactions import login
from common.models import User
from party.models import Party


@pytest.mark.django_db
def test_add_character_to_existing_group(selenium: WebDriver, live_server: LiveServer):
    call_command("loaddata", "initial_data")

    username, password = "gm", "password"
    gm = User.objects.create_user(username, password=password)
    player = User.objects.create_user("player")
    character = baker.make(Character, player=player)
    party = baker.make(Party, game_master=gm)

    selenium.get(live_server.url)
    login(selenium, username, password)

    selenium.get(live_server.url + reverse("party:list"))
    selenium.find_element(
        By.CSS_SELECTOR, f".party[data-id='{party.pk}'] .edit"
    ).click()
    invited = Select(selenium.find_element(By.ID, "id_invited_characters"))
    invited.select_by_index(0)
    selenium.find_element(By.CSS_SELECTOR, "[type=submit]").click()

    assert selenium.current_url == live_server.url + reverse("party:list")
    party.refresh_from_db()
    assert set(party.invited_characters.all()) == {character}


@pytest.mark.django_db
def test_gm_observe_invited_character_in_group(
    selenium: WebDriver, live_server: LiveServer
):
    call_command("loaddata", "initial_data")

    username, password = "gm", "password"
    gm = User.objects.create_user(username, password=password)
    player = User.objects.create_user("player")
    party = baker.make(Party, game_master=gm)
    character = baker.make(Character, player=player)
    party.invited_characters.add(character)

    selenium.get(live_server.url)
    login(selenium, username, password)

    selenium.get(live_server.url + reverse("party:list"))
    selenium.find_element(
        By.CSS_SELECTOR, f".party[data-id='{party.pk}'] .access"
    ).click()
    selenium.find_element(
        By.CSS_SELECTOR, f".character[data-id='{character.pk}'] .observe"
    ).click()
    title = selenium.find_element(By.TAG_NAME, "h1").text.strip()
    assert title == character.name


@pytest.mark.django_db
def test_gm_observe_invited_character_in_two_groups(
    selenium: WebDriver, live_server: LiveServer
):
    call_command("loaddata", "initial_data")

    username, password = "gm", "password"
    gm = User.objects.create_user(username, password=password)
    player = User.objects.create_user("player")
    party = baker.make(Party, game_master=gm)
    other_party = baker.make(Party, game_master=gm)
    character = baker.make(Character, player=player)
    party.invited_characters.add(character)
    other_party.invited_characters.add(character)

    selenium.get(live_server.url)
    login(selenium, username, password)

    selenium.get(live_server.url + reverse("party:list"))
    selenium.find_element(
        By.CSS_SELECTOR, f".party[data-id='{party.pk}'] .access"
    ).click()
    selenium.find_element(
        By.CSS_SELECTOR, f".character[data-id='{character.pk}'] .observe"
    ).click()
    title = selenium.find_element(By.TAG_NAME, "h1").text.strip()
    assert title == character.name
