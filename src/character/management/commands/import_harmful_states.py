from django.core.management import BaseCommand
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

from character.models.character import HarmfulState


class Command(BaseCommand):
    def handle(self, *args, **options) -> None:  # noqa: ARG002
        url = "https://www.co-drs.org/fr/jeu/etats-prejudiciables"
        self.setup_selenium()
        self.selenium.get(url)
        states = self.selenium.find_elements(By.CSS_SELECTOR, "tbody tr")
        for state in states:
            try:
                self.import_row(url, state)
            except Exception as e:
                self.stderr.write(f"{type(e)}: {e}")
        self.stdout.write(f"Finished processing {len(states)} states.")

    def import_row(self, url: str, state_row: WebElement) -> None:
        name = state_row.find_element(By.CLASS_NAME, "views-field-name").text.strip()
        description = state_row.find_element(
            By.CLASS_NAME,
            "views-field-description__value",
        ).text.strip()
        icon_url = state_row.find_element(
            By.CSS_SELECTOR,
            ".views-field-field-svg-icon img",
        ).get_dom_attribute("src")
        state, _ = HarmfulState.objects.update_or_create(
            name=name,
            defaults={"description": description, "url": url, "icon_url": icon_url},
        )
        self.stdout.write(self.style.SUCCESS(f"Created/updated state {state}"))

    def setup_selenium(self) -> None:
        options = webdriver.FirefoxOptions()
        options.add_argument("-headless")
        self.selenium = webdriver.Firefox(options=options)
