import random

import pytest
from django.urls import reverse
from model_bakery import baker
from pytest_django.live_server_helper import LiveServer
from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.webdriver import WebDriver
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.wait import WebDriverWait

from character.models import Character, Profile
from character.tests.test_interactions import create_hurt_character, login
from common.models import User
from party.models import BattleEffect, Party


@pytest.mark.django_db
def test_add_character_to_existing_group(selenium: WebDriver, live_server: LiveServer):
    username, password = "gm", "password"
    gm = User.objects.create_user(username, password=password)
    player = User.objects.create_user("player")
    character = baker.make(Character, player=player)
    party = baker.make(Party, game_master=gm)

    login(selenium, live_server, username, password)

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
    username, password = "gm", "password"
    gm = User.objects.create_user(username, password=password)
    player = User.objects.create_user("player")
    party = baker.make(Party, game_master=gm)
    character = baker.make(Character, player=player)
    party.invited_characters.add(character)

    login(selenium, live_server, username, password)

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
    username, password = "gm", "password"
    gm = User.objects.create_user(username, password=password)
    player = User.objects.create_user("player")
    party = baker.make(Party, game_master=gm)
    other_party = baker.make(Party, game_master=gm)
    character = baker.make(Character, player=player)
    party.invited_characters.add(character)
    other_party.invited_characters.add(character)

    login(selenium, live_server, username, password)

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
def test_reset_stats_view(
    selenium: WebDriver, live_server: LiveServer, initial_data: None
):
    user, password = "gm", "password"
    gm = User.objects.create_user(user, password=password)
    assert Profile.objects.count() > 1
    for profile in Profile.objects.all():
        player = User.objects.create_user(f"user{profile}", password="password")
        create_hurt_character(player, profile)
    party = baker.make(Party, game_master=gm)
    party.characters.set(Character.objects.all())

    login(selenium, live_server, user, password)

    url = reverse("party:details", kwargs={"pk": party.pk})
    selenium.get(live_server.url + url)
    selenium.find_element(By.ID, "reset-stats").click()
    selenium.find_element(By.CSS_SELECTOR, "[type=submit]").click()
    assert selenium.current_url == live_server.url + party.get_absolute_url()

    for character in Character.objects.all():
        assert character.health_remaining == character.health_max
        assert character.mana_remaining == character.mana_max
        assert character.recovery_points_remaining == character.recovery_points_max
        assert character.luck_points_remaining == character.luck_points_max


@pytest.mark.django_db
def test_player_can_add_effect_to_group(selenium: WebDriver, live_server: LiveServer):
    """Any member of a group can add effects to the group."""
    user, password = "player", "password"
    player = User.objects.create_user(user, password=password)
    character = baker.make(Character, player=player)
    party = baker.make(Party)
    party.characters.add(character)

    assert BattleEffect.objects.count() == 0

    name = "Agrandissement"
    target = "Joueur 4"
    description = (
        "Le Magicien ou une cible volontaire (au contact) voit sa taille augmenter de "
        "50% pendant [5 + Mod. d'INT] tours. Il gagne +2 aux DM au contact et aux "
        "tests de FOR. Pataud, il subit un malus de -2 aux tests de DEX."
    )
    remaining_rounds = "8"

    go_to_party(selenium, live_server, party, user, password)
    fill_effect(selenium, name, description, target, remaining_rounds)
    effect = assert_effect_is_created(name, description, target, remaining_rounds)
    element = selenium.find_element(By.CSS_SELECTOR, f'.effect[data-id="{effect.pk}"]')
    assert effect.name in element.text
    assert effect.target in element.text
    assert effect.description in element.text


@pytest.mark.django_db
def test_gm_can_add_effect_to_group(selenium: WebDriver, live_server: LiveServer):
    """The GM of a group can add effects to the group."""
    user, password = "gm", "password"
    gm = User.objects.create_user(user, password=password)
    party = baker.make(Party, game_master=gm)

    assert BattleEffect.objects.count() == 0

    name = "Brûlé"
    target = "Boss 2"
    description = (
        "Le Magicien choisit une cible située à moins de 30 mètres. Si son attaque "
        "magique réussit, la cible encaisse [1d6 + Mod. d'INT] DM et la flèche "
        "enflamme ses vêtements. Chaque tour de combat suivant, le feu inflige 1d6 "
        "dégâts supplémentaires. Sur un résultat de 1 à 2, les flammes s'éteignent et "
        "le sort prend fin."
    )
    remaining_rounds = "-1"

    go_to_party(selenium, live_server, party, user, password)
    fill_effect(selenium, name, description, target, remaining_rounds)
    effect = assert_effect_is_created(name, description, target, remaining_rounds)
    element = selenium.find_element(By.CSS_SELECTOR, f'.effect[data-id="{effect.pk}"]')
    assert effect.name in element.text
    assert effect.target in element.text
    assert effect.description in element.text


@pytest.mark.django_db
def test_gm_can_change_remaining_rounds(selenium: WebDriver, live_server: LiveServer):
    """The GM of a group can increase or decrease the remaining rounds of effects."""
    user, password = "gm", "password"
    gm = User.objects.create_user(user, password=password)
    party = baker.make(Party, game_master=gm)

    active_not_nearly_terminated = baker.make(  # noqa: F841
        BattleEffect,
        _quantity=7,
        remaining_rounds=lambda: random.randint(3, 12),
        party=party,
    )
    active_nearly_terminated = baker.make(  # noqa: F841
        BattleEffect, _quantity=3, remaining_rounds=1, party=party
    )
    terminated = baker.make(  # noqa: F841
        BattleEffect, _quantity=5, remaining_rounds=0, party=party
    )
    permanent = baker.make(  # noqa: F841
        BattleEffect, _quantity=2, remaining_rounds=-1, party=party
    )
    not_party = baker.make(BattleEffect, _quantity=4, remaining_rounds=55)  # noqa: F841
    beacon = active_nearly_terminated[0]
    selector = f'.effect[data-id="{beacon.pk}"] .card-footer'

    def beacon_has_text(text: str):
        def wrapped(driver: WebDriver):
            return driver.find_element(By.CSS_SELECTOR, selector).text == text

        return wrapped

    go_to_party(selenium, live_server, party, user, password)
    selenium.find_element(By.ID, "increase-rounds").click()
    WebDriverWait(selenium, 3).until(beacon_has_text("2 tours"))
    assert BattleEffect.objects.filter(party=party).permanent().count() == 2
    assert (
        BattleEffect.objects.filter(party=party, remaining_rounds__gt=1).count() == 10
    )
    assert BattleEffect.objects.filter(party=party, remaining_rounds=1).count() == 5
    assert BattleEffect.objects.filter(party=party).terminated().count() == 0
    assert (
        BattleEffect.objects.exclude(party=party).filter(remaining_rounds=55).count()
        == 4
    )

    selenium.find_element(By.ID, "decrease-rounds").click()
    WebDriverWait(selenium, 3).until(beacon_has_text("Dernier"))
    assert BattleEffect.objects.filter(party=party).permanent().count() == 2
    assert BattleEffect.objects.filter(party=party, remaining_rounds__gt=1).count() == 7
    assert BattleEffect.objects.filter(party=party, remaining_rounds=1).count() == 3
    assert BattleEffect.objects.filter(party=party).terminated().count() == 5
    assert (
        BattleEffect.objects.exclude(party=party).filter(remaining_rounds=55).count()
        == 4
    )

    selenium.find_element(By.ID, "decrease-rounds").click()
    WebDriverWait(selenium, 3).until(beacon_has_text("Terminé !"))
    assert BattleEffect.objects.filter(party=party).permanent().count() == 2
    assert BattleEffect.objects.filter(party=party).active().count() == 7
    assert BattleEffect.objects.filter(party=party, remaining_rounds=1).count() == 0
    assert BattleEffect.objects.filter(party=party).terminated().count() == 8
    assert (
        BattleEffect.objects.exclude(party=party).filter(remaining_rounds=55).count()
        == 4
    )


@pytest.mark.django_db
def test_gm_can_delete_any_existing_effect(
    selenium: WebDriver, live_server: LiveServer
):
    """The GM of a group can delete any existing effect, running or terminated."""
    user, password = "gm", "password"
    gm = User.objects.create_user(user, password=password)
    party = baker.make(Party, game_master=gm)
    effects = baker.make(BattleEffect, _quantity=2, party=party)

    assert BattleEffect.objects.count() == 2

    go_to_party(selenium, live_server, party, user, password)
    selenium.find_element(
        By.CSS_SELECTOR, f'.effect[data-id="{effects[0].pk}"] .delete'
    ).click()

    assert BattleEffect.objects.count() == 1
    BattleEffect.objects.get(pk=effects[1].pk)


@pytest.mark.django_db
def test_player_cant_change_existing_running_effect(
    selenium: WebDriver, live_server: LiveServer
):
    """Members of the group can only view existing running effects, no update."""
    user, password = "player", "password"
    player = User.objects.create_user(user, password=password)
    character = baker.make(Character, player=player)
    party = baker.make(Party)
    party.characters.set([character])
    effects = baker.make(BattleEffect, _quantity=2, party=party)

    go_to_party(selenium, live_server, party, user, password)
    effect = effects[0]
    effect_element = selenium.find_element(
        By.CSS_SELECTOR, f'.effect[data-id="{effect.pk}"]'
    )
    assert effect.name in effect_element.text
    assert effect.target in effect_element.text
    assert effect.description in effect_element.text

    with pytest.raises(NoSuchElementException):
        selenium.find_element(By.CSS_SELECTOR, ".effect .delete")
    with pytest.raises(NoSuchElementException):
        selenium.find_element(By.ID, "increase-rounds")
    with pytest.raises(NoSuchElementException):
        selenium.find_element(By.ID, "decrease-rounds")


def fill_effect(
    selenium: WebDriver, name: str, description: str, target: str, remaining_rounds: str
) -> None:
    selenium.find_element(By.ID, "add-effect").click()
    selenium.find_element(By.ID, "id_name").send_keys(name)
    selenium.find_element(By.ID, "id_target").send_keys(target)
    selenium.find_element(By.ID, "id_description").send_keys(description)
    rounds_element = selenium.find_element(By.ID, "id_remaining_rounds")
    rounds_element.clear()
    rounds_element.send_keys(remaining_rounds)
    selenium.find_element(By.CSS_SELECTOR, "button[type=submit]").click()


def assert_effect_is_created(
    name: str, description: str, target: str, remaining_rounds: str
) -> BattleEffect:
    assert BattleEffect.objects.count() == 1
    effect = BattleEffect.objects.first()
    assert effect.name == name
    assert effect.target == target
    assert effect.description == description
    assert str(effect.remaining_rounds) == remaining_rounds
    return effect


def go_to_party(
    selenium: WebDriver, live_server: LiveServer, party: Party, user: str, password: str
) -> None:
    login(selenium, live_server, user, password)
    url = reverse("party:details", kwargs={"pk": party.pk})
    selenium.get(live_server.url + url)
