from django.core.management import call_command
from model_bakery import baker
from pytest_django.live_server_helper import LiveServer
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.webdriver import WebDriver

from character.models import Character
from character.tests.test_interactions import login
from common.models import User


def test_pet_happy_path(selenium: WebDriver, live_server: LiveServer):
    # Load fixtures
    call_command("loaddata", "initial_data")

    # Create a user
    username, password = "user", "some_password"
    player = User.objects.create_user(username, password=password)
    character = baker.make(Character, player=player)
    login(selenium, live_server, username, password)

    # Starting on the character's sheet.
    selenium.get(live_server.url + character.get_absolute_url())

    # Click on the button to add a pet.
    selenium.find_element(By.ID, "add-pet").click()

    pet_start_health = 10

    # A form appears, asking the pet's details.
    # Fill the form.
    # Fields are: name, health_max, health_remaining, modifier_strength,
    # modifier_dexterity, modifier_constitution, modifier_intelligence,
    # modifier_wisdom, modifier_charisma, damage, initiative, defense, attack,
    # recovery and notes.
    selenium.find_element(By.ID, "id_name").send_keys("My pet")
    selenium.find_element(By.ID, "id_health_max").send_keys(str(pet_start_health))
    selenium.find_element(By.ID, "id_health_remaining").send_keys(str(pet_start_health))
    selenium.find_element(By.ID, "id_modifier_strength").send_keys("-3")
    selenium.find_element(By.ID, "id_modifier_dexterity").send_keys("-2")
    selenium.find_element(By.ID, "id_modifier_constitution").send_keys("-1")
    selenium.find_element(By.ID, "id_modifier_intelligence").send_keys("1")
    selenium.find_element(By.ID, "id_modifier_wisdom").send_keys("2")
    selenium.find_element(By.ID, "id_modifier_charisma").send_keys("3")
    selenium.find_element(By.ID, "id_damage").send_keys("4")
    selenium.find_element(By.ID, "id_initiative").send_keys("5")
    selenium.find_element(By.ID, "id_defense").send_keys("6")
    selenium.find_element(By.ID, "id_attack").send_keys("7")
    selenium.find_element(By.ID, "id_recovery").send_keys("1 heure 1 dé de vie")
    selenium.find_element(By.ID, "id_notes").send_keys("My pet's notes")

    # Save & check redirected to character's sheet.
    selenium.find_element(By.CSS_SELECTOR, "[type=submit]").click()
    assert selenium.current_url == live_server.url + character.get_absolute_url()

    # Fetch pet
    pet = character.pets.first()

    # It now displays the pet's information.
    # There can be multiple pets.
    assert (
        selenium.find_element(
            By.CSS_SELECTOR,
            f".pet[data-id='{pet.pk}'] .pet-name",
        ).text
        == "My pet"
    )

    # The GM and I can edit my pet's life points,
    # in order to follow them during the fight.
    selenium.find_element(
        By.CSS_SELECTOR,
        f".pet[data-id='{pet.pk}'] .health .decrease",
    ).click()
    pet.refresh_from_db()
    assert pet.health_remaining == pet_start_health - 1

    # I can edit my pets. When I click on the edit button of a pet,
    # I have the same form as previously, pre-filled with the current values of my pet.
    selenium.find_element(By.CSS_SELECTOR, f".pet[data-id='{pet.pk}'] .edit").click()
    pet_name = selenium.find_element(By.ID, "id_name")
    assert pet_name.get_attribute("value") == "My pet"
    assert selenium.find_element(By.ID, "id_health_max").get_attribute("value") == "10"
    assert (
        selenium.find_element(By.ID, "id_health_remaining").get_attribute("value")
        == "9"
    )
    pet_name.clear()
    pet_name.send_keys("new name")
    selenium.find_element(By.CSS_SELECTOR, "[type=submit]").click()
    pet.refresh_from_db()
    assert pet.name == "new name"

    # I can delete my pets. When I click on the pet's delete button,
    # I'm redirected to a page asking confirmation of my action,
    # in order to avoid mistakes.
    selenium.find_element(By.CSS_SELECTOR, f".pet[data-id='{pet.pk}'] .delete").click()
    assert character.pets.count() == 1
    selenium.find_element(By.CSS_SELECTOR, "[type=submit]").click()
    assert selenium.current_url == live_server.url + character.get_absolute_url()
    assert character.pets.count() == 0
