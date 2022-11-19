import pytest
from django.core.management import call_command
from django.urls import reverse
from model_bakery import baker
from pytest_django.live_server_helper import LiveServer
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.webdriver import WebDriver

from character.models import Character
from common.models import User


@pytest.mark.django_db
def test_create_character(selenium: WebDriver, live_server: LiveServer):
    # Load fixtures
    call_command("loaddata", "initial_data")

    # Create a user
    username, password = "user", "some_password"
    player = User.objects.create_user(username, password=password)

    # Go to home page
    login(selenium, live_server, username, password)

    # Click on new character
    selenium.find_element(By.ID, "new-character").click()

    # Check no existing character
    assert Character.objects.count() == 0

    # Fill form with missing age
    raw_values = {
        "name": "My Character",
        "equipment": "Lighter, blanket",
        "damage_reduction": "Something here",
        "level": 8,
        "height": 134,
        "weight": 78,
        "value_strength": 9,
        "value_dexterity": 12,
        "value_constitution": 15,
        "value_intelligence": 13,
        "value_wisdom": 19,
        "value_charisma": 10,
        "armor": 5,
        "shield": 6,
        "defense_misc": 7,
        "health_max": 67,
        "money_pp": 1,
        "money_po": 2,
        "money_pa": 3,
        "money_pc": 4,
    }
    for name, value in raw_values.items():
        element = selenium.find_element(By.ID, f"id_{name}")
        element.clear()
        element.send_keys(str(value))

    related_values = {
        "race": "Gnome",
        "profile": "Druide",
        "racial_capability": "Don étrange",
    }
    for name, value in related_values.items():
        element = selenium.find_element(By.ID, f"id_{name}")
        element.send_keys(str(value))

    # Save
    url = selenium.current_url
    selenium.find_element(By.CSS_SELECTOR, "button[type=submit]").click()

    # Assert URL hasn't changed
    assert selenium.current_url == url

    # Fill level
    level_element = selenium.find_element(By.ID, "id_age")
    level_element.clear()
    level_element.send_keys("32")

    # Save
    selenium.find_element(By.CSS_SELECTOR, "button[type=submit]").click()

    # Assert redirected on list view
    assert selenium.current_url == live_server.url + reverse("character:list")

    # Assert character in DB, belongs to user
    assert Character.objects.count() == 1
    character = Character.objects.get()
    assert character.player == player
    for name, value in raw_values.items():
        assert getattr(character, name) == value


@pytest.mark.django_db
def test_list_characters(selenium: WebDriver, live_server: LiveServer):
    # Load fixtures
    call_command("loaddata", "initial_data")
    # Create user 1
    username, password = "user1", "some_password"
    player = User.objects.create_user(username, password=password)

    # Create user 2
    other = User.objects.create_user("user2", password=password)

    # Create two characters (1, 2) for user 1
    characters = baker.make(Character, _quantity=2, player=player)

    # Create a character (3) for user 2
    baker.make(Character, player=other)

    # Go to home page
    login(selenium, live_server, username, password)

    # Assert only characters 1 and 2 are shown although there are 3 characters in DB
    assert Character.objects.count() == 3
    names = {
        name.text
        for name in selenium.find_elements(
            By.CSS_SELECTOR, ".character.card .card-title"
        )
    }
    expected_names = {character.name for character in characters}
    assert names == expected_names


@pytest.mark.django_db
def test_delete_character(selenium: WebDriver, live_server: LiveServer):
    call_command("loaddata", "initial_data")

    username, password = "user", "some_password"
    player = User.objects.create_user(username, password=password)
    characters = baker.make(Character, _quantity=2, player=player)

    login(selenium, live_server, username, password)

    assert Character.objects.count() == 2
    selenium.find_element(
        By.CSS_SELECTOR, f".character.card[data-id='{characters[0].pk}'] .delete"
    ).click()
    selenium.find_element(By.CSS_SELECTOR, "[type=submit]").click()

    assert selenium.current_url == live_server.url + reverse("character:list")
    assert Character.objects.count() == 1
    assert Character.objects.filter(pk=characters[0].pk).first() is None


def login(
    selenium: WebDriver, live_server: LiveServer, username: str, password: str
) -> None:
    selenium.get(live_server.url)
    selenium.find_element(By.ID, "login").click()
    selenium.find_element(By.ID, "id_username").send_keys(username)
    selenium.find_element(By.ID, "id_password").send_keys(password)
    selenium.find_element(By.CSS_SELECTOR, "button[type=submit]").click()
