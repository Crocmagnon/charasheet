from django import forms
from django.core.exceptions import ValidationError

from party.models import Party


class PartyForm(forms.ModelForm):
    class Meta:
        model = Party
        fields = ["name", "invited_characters"]

    def clean_invited_characters(self):
        invited = self.cleaned_data["invited_characters"]
        if not self.instance:
            return invited
        members = self.instance.characters.all()
        for character in invited:
            if character in members:
                self.add_error(
                    "invited_characters",
                    ValidationError(f"{character} is already a group member."),
                )
        return invited
