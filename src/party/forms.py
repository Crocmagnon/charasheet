from django import forms
from django.core.exceptions import ValidationError
from django.db.models import Q

from character.models import Character
from party.models import BattleEffect, Party


class PartyForm(forms.ModelForm):
    def __init__(self, *args, **kwargs) -> None:
        self.original_instance = kwargs.get("instance")
        super().__init__(*args, **kwargs)
        qs = Character.objects.all()
        if self.original_instance:
            qs = qs.filter(
                Q(private=False)
                | Q(
                    pk__in=self.original_instance.invited_characters.all().values_list(
                        "pk",
                        flat=True,
                    ),
                ),
            )
        self.fields["invited_characters"].queryset = qs

    class Meta:
        model = Party
        fields = ["name", "invited_characters"]

    def clean_invited_characters(self):
        invited = self.cleaned_data["invited_characters"]
        if not self.original_instance:
            return invited
        members = self.original_instance.characters.all()
        for character in invited:
            if character in members:
                self.add_error(
                    "invited_characters",
                    ValidationError(f"{character} is already a group member."),
                )
        return invited


class BattleEffectForm(forms.ModelForm):
    class Meta:
        model = BattleEffect
        fields = ["name", "target", "description", "remaining_rounds"]
