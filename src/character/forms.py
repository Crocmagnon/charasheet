from django import forms
from django.core.exceptions import ValidationError
from django.db.models import Q

from character.models import Character, Path


class EquipmentForm(forms.ModelForm):
    class Meta:
        model = Character
        fields = ["equipment", "money_pp", "money_po", "money_pa", "money_pc"]


class AddPathForm(forms.Form):
    character_path = forms.ModelChoiceField(
        Path.objects.none(),
        required=False,
        empty_label="----- Voies liées au personnage -----",
    )
    other_path = forms.ModelChoiceField(
        Path.objects.none(), required=False, empty_label="----- Autres voies -----"
    )

    def __init__(self, character: Character, *args, **kwargs):
        super().__init__(*args, **kwargs)
        paths = {cap.path_id for cap in character.capabilities.all()}
        paths = (
            Path.objects.exclude(pk__in=paths)
            .order_by("profile__name", "race__name")
            .select_related("profile", "race")
        )
        character_paths = paths.filter(
            Q(profile=character.profile) | Q(race=character.race)
        )
        self.fields["character_path"].queryset = character_paths
        self.fields["character_path"].widget.attrs["class"] = "form-select"
        self.fields["other_path"].queryset = paths.exclude(
            pk__in={path.pk for path in character_paths}
        )
        self.fields["other_path"].widget.attrs["class"] = "form-select"

    def clean(self):
        cleaned_data = super().clean()
        values = [cleaned_data.get("character_path"), cleaned_data.get("other_path")]
        if len(list(filter(None, values))) != 1:
            raise ValidationError("Vous devez sélectionner une seule valeur.")
        return cleaned_data
