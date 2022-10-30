from django import forms

from character.models import Character


class EquipmentForm(forms.ModelForm):
    class Meta:
        model = Character
        fields = ["equipment", "money_pp", "money_po", "money_pa", "money_pc"]
