import pytest
from model_bakery import baker

from character.models import Character
from common.models import User
from party.models import Party


@pytest.mark.django_db
def test_can_access_own_character(client):
    # Create a user
    player = User.objects.create_user("username", password="password")

    character = baker.make(Character, player=player)
    client.force_login(player)
    res = client.get(character.get_absolute_url())
    assert res.status_code == 200


@pytest.mark.django_db
def test_cant_access_random_character(client):
    # Create a user
    player = User.objects.create_user("user", password="password")
    other = User.objects.create_user("other", password="password")

    character = baker.make(Character, player=other)
    client.force_login(player)
    res = client.get(character.get_absolute_url())
    assert res.status_code == 404


@pytest.mark.django_db
def test_can_access_character_in_party(client):
    # Create a user
    player = User.objects.create_user("user", password="password")
    friend = User.objects.create_user("friend", password="password")

    character = baker.make(Character, player=player)
    friend_character = baker.make(Character, player=friend)
    party = baker.make(Party)
    party.characters.add(character)
    party.characters.add(friend_character)
    client.force_login(player)
    res = client.get(character.get_absolute_url())
    assert res.status_code == 200
