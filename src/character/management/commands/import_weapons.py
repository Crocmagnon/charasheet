from django.core.management import BaseCommand
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

from character.models import Weapon


class Command(BaseCommand):
    def handle(self, *args, **options) -> None:
        url = "https://www.co-drs.org/fr/ressources/equipements/armes"
        self.setup_selenium()
        self.selenium.get(url)
        states = self.selenium.find_elements(By.CSS_SELECTOR, "tbody tr")
        for state in states:
            try:
                self.import_row(url, state)
            except Exception as e:
                print(f"{type(e)}: {e}")
        self.stdout.write(f"Finished processing {len(states)} weapons.")

    def import_row(self, url: str, state_row: WebElement) -> None:
        name = state_row.find_element(By.CLASS_NAME, "views-field-name").text.strip()
        category = (
            state_row.find_element(By.CLASS_NAME, "views-field-type")
            .text.strip()
            .lower()
        )
        if "distance" in category:
            category = Weapon.Category.RANGE
        else:
            category = Weapon.Category.MELEE
        damage = state_row.find_element(By.CLASS_NAME, "views-field-dmg").text.strip()
        weapon, _ = Weapon.objects.update_or_create(
            name=name,
            defaults={
                "damage": damage,
                "special": "",
                "category": category,
                "url": url,
            },
        )
        self.stdout.write(self.style.SUCCESS(f"Created/updated weapon {weapon}"))

    def setup_selenium(self) -> None:
        options = webdriver.FirefoxOptions()
        options.add_argument("-headless")
        self.selenium = webdriver.Firefox(options=options)
