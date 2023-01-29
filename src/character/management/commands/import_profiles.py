from django.core.management import BaseCommand
from selenium import webdriver
from selenium.webdriver.common.by import By

from character.models import Profile
from character.models.dice import Dice


class Command(BaseCommand):
    def handle(self, *args, **options) -> None:  # noqa: ARG002
        url = "https://www.co-drs.org/fr/jeu/profils"
        self.setup_selenium()
        self.selenium.get(url)
        anchors = self.selenium.find_elements(By.CSS_SELECTOR, ".card-img-top a")
        urls = [anchor.get_attribute("href") for anchor in anchors]
        for url in urls:
            try:
                self.import_profile(url)
            except Exception as e:
                self.stderr.write(f"{type(e)}: {e}")

    def import_profile(self, url: str) -> None:
        self.selenium.get(url)
        name = self.selenium.find_element(By.TAG_NAME, "h1").text
        dice = self.get_dice(name)
        magical_strength = self.get_magical_strength()
        notes = self.get_notes(name)
        mana_max_compute = self.get_mana_max_compute(name)

        profile, _ = Profile.objects.update_or_create(
            name=name,
            defaults={
                "life_dice": dice,
                "magical_strength": magical_strength,
                "notes": notes,
                "url": url,
                "mana_max_compute": mana_max_compute,
            },
        )
        self.stdout.write(self.style.SUCCESS(f"Created/updated profile {profile}"))

    def get_dice(self, name: str) -> Dice:
        dice = self.selenium.find_element(By.CSS_SELECTOR, ".dice + div").text.split(
            "D"
        )
        number_of_dice, dice_value = int(dice[0]), int(dice[1])
        if number_of_dice != 1:
            self.stdout.write(
                self.style.WARNING(f"Multiple dice for {name}: {number_of_dice}")
            )
        return Dice(dice_value)

    def get_magical_strength(self) -> Profile.MagicalStrength:
        try:
            magical_strength = self.selenium.find_element(
                By.CSS_SELECTOR, ".field--name-magic-attack-modifier .field__item"
            ).text
            magical_strength = Profile.MagicalStrength(magical_strength)
        except Exception:
            magical_strength = Profile.MagicalStrength.NONE
        return magical_strength

    def get_notes(self, name: str) -> str:
        notes = ""
        fields = ["weapons-and-armors", "starting-equipment"]
        for field_name in fields:
            try:
                field_class = f"field--name-{field_name}"
                field = self.selenium.find_element(By.CLASS_NAME, field_class)
                title = field.find_element(By.CLASS_NAME, "field__label").text
                text = field.find_element(By.CLASS_NAME, "field__item").text
                notes += f"\n\n# {title}\n{text}"
            except Exception:
                self.stdout.write(f"No {field_name} found for {name}")
        notes = notes.strip()
        return notes

    def get_mana_max_compute(self, name) -> Profile.ManaMax:
        if name in ["Barde", "Druide", "Forgesort", "Prêtre"]:
            return Profile.ManaMax.LEVEL
        if name in ["Ensorceleur", "Magicien", "Nécromancien"]:
            return Profile.ManaMax.DOUBLE_LEVEL
        return Profile.ManaMax.NO_MANA

    def setup_selenium(self) -> None:
        options = webdriver.FirefoxOptions()
        options.add_argument("-headless")
        self.selenium = webdriver.Firefox(options=options)
