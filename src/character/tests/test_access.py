from http import HTTPStatus

import pytest
from model_bakery import baker

from character.models import Character
from common.models import User
from party.models import Party


@pytest.mark.django_db()
def test_can_access_own_character(client):
    player = User.objects.create_user("username", password="password")

    notes = "Some notes"
    gm_notes = "Some GM notes"
    character = baker.make(Character, player=player, notes=notes, gm_notes=gm_notes)
    client.force_login(player)
    res = client.get(character.get_absolute_url())
    assert res.status_code == HTTPStatus.OK

    body = res.content.decode("utf-8")
    assert notes in body
    assert gm_notes not in body


@pytest.mark.django_db()
def test_cant_access_random_character(client):
    player = User.objects.create_user("user", password="password")
    other = User.objects.create_user("other", password="password")

    character = baker.make(Character, player=other)
    client.force_login(player)
    res = client.get(character.get_absolute_url())
    assert res.status_code == HTTPStatus.NOT_FOUND


@pytest.mark.django_db()
def test_can_access_character_in_party(client):
    player = User.objects.create_user("user", password="password")
    friend = User.objects.create_user("friend", password="password")

    character = baker.make(Character, player=player)
    notes = "Some notes"
    gm_notes = "Some GM notes"
    friend_character = baker.make(
        Character,
        player=friend,
        notes=notes,
        gm_notes=gm_notes,
    )
    party = baker.make(Party)
    party.characters.add(character)
    party.characters.add(friend_character)
    client.force_login(player)
    res = client.get(friend_character.get_absolute_url())
    assert res.status_code == HTTPStatus.OK

    body = res.content.decode("utf-8")
    assert notes not in body
    assert gm_notes not in body


@pytest.mark.django_db()
def test_game_master_can_access_character_in_party(client):
    player = User.objects.create_user("user", password="password")
    gm = User.objects.create_user("gm", password="password")

    notes = "Some notes"
    gm_notes = "Some GM notes"
    character = baker.make(Character, player=player, notes=notes, gm_notes=gm_notes)
    party = baker.make(Party, game_master=gm)
    party.characters.add(character)
    client.force_login(gm)
    res = client.get(character.get_absolute_url())
    assert res.status_code == HTTPStatus.OK

    body = res.content.decode("utf-8")
    assert notes in body
    assert gm_notes in body
