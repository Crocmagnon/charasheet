from model_bakery import baker

from character.models import Character
from common.models import User
from party.models import Party


def test_party_managed_by(db):
    game_master = User.objects.create_user("game_master")
    other_user = User.objects.create_user("other")
    expected = Party.objects.create(name="some name", game_master=game_master)
    Party.objects.create(name="some other name", game_master=other_user)
    related_to = Party.objects.managed_by(game_master)
    assert len(related_to) == 1
    assert related_to[0] == expected


def test_party_played_by(db):
    player = User.objects.create_user("game_master")
    player_character = baker.make(Character, player=player)
    other_user = User.objects.create_user("other")
    other_character = baker.make(Character, player=other_user)

    expected = Party.objects.create(name="some name", game_master=other_user)
    expected.characters.add(player_character)
    other_party = Party.objects.create(name="some other name", game_master=other_user)
    other_party.characters.add(other_character)
    related_to = Party.objects.played_by(player)
    assert len(related_to) == 1
    assert related_to[0] == expected
