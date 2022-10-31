from django import forms

from character.models import Character, Path


class EquipmentForm(forms.ModelForm):
    class Meta:
        model = Character
        fields = ["equipment", "money_pp", "money_po", "money_pa", "money_pc"]


class AddPathForm(forms.Form):
    path = forms.ModelChoiceField(Path.objects.none())

    def __init__(self, character: Character, *args, **kwargs):
        super().__init__(*args, **kwargs)
        paths = {cap.path_id for cap in character.capabilities.all()}
        self.fields["path"].queryset = Path.objects.exclude(pk__in=paths).order_by(
            "profile__name", "race__name"
        )
        self.fields["path"].widget.attrs["class"] = "form-select"
