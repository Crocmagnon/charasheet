import pytest
from django.core.management import call_command
from django.urls import reverse
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
    selenium.get(live_server.url)

    # Login as user
    selenium.find_element(By.ID, "login").click()
    selenium.find_element(By.ID, "id_username").send_keys(username)
    selenium.find_element(By.ID, "id_password").send_keys(password)
    selenium.find_element(By.CSS_SELECTOR, "button[type=submit]").click()

    # Click on new character
    selenium.find_element(By.ID, "new-character").click()

    # Check no existing character
    assert Character.objects.count() == 0

    # Fill form
    raw_values = {
        "name": "My Character",
        "equipment": "Lighter, blanket",
        "damage_reduction": "Something here",
        "level": 8,
        "age": 32,
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
    related_values = {
        "race": "Gnome",
        "profile": "Druide",
        "racial_capability": "Don étrange",
    }
    for name, value in raw_values.items():
        element = selenium.find_element(By.ID, f"id_{name}")
        element.clear()
        element.send_keys(str(value))
    for name, value in related_values.items():
        element = selenium.find_element(By.ID, f"id_{name}")
        element.send_keys(str(value))

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
