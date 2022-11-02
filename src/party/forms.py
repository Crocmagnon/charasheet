from django import forms

from party.models import Party


class PartyForm(forms.ModelForm):
    class Meta:
        model = Party
        fields = ["name", "characters"]
