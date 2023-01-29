from django.core.management import BaseCommand
from selenium import webdriver
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

from character.models import Capability, Path


class Command(BaseCommand):
    def handle(self, *args, **options) -> None:  # noqa: ARG002
        url = "https://www.co-drs.org/fr/jeu/capacites"
        self.setup_selenium()
        self.selenium.get(url)
        cards = []
        expected_capability_count = 430
        while len(cards) < expected_capability_count:
            self.selenium.find_element(By.TAG_NAME, "body").send_keys(Keys.END)
            cards = self.selenium.find_elements(
                By.CSS_SELECTOR, ".col-md-4.col-sm-6.col-12.mb-4.views-row"
            )
        for card in cards:
            try:
                self.import_capability(card)
            except Exception as e:
                self.stderr.write(f"{type(e)}: {e}")
        self.stdout.write(f"Finished processing {len(cards)} caps.")

    def import_capability(self, card: WebElement):
        title = (
            card.find_element(By.CSS_SELECTOR, ".card-front .card-title .fw-bold")
            .text.strip()
            .split(" | ")
        )
        name = title[0].replace("’", "'").strip()
        rank = int(title[1].replace("rang ", ""))
        paths = self.get_paths(card, name)
        limited = False
        if "(L)" in name:
            limited = True
            name = name.replace("(L)", "")
        spell = False
        if "*" in name:
            spell = True
            name = name.replace("*", "")
        name = name.strip()
        description = (
            card.find_element(By.CLASS_NAME, "field--name-description")
            .text.strip()
            .replace("’", "'")
        )
        for path in paths:
            try:
                capability, _ = Capability.objects.update_or_create(
                    rank=rank,
                    path=path,
                    defaults={
                        "name": name,
                        "limited": limited,
                        "spell": spell,
                        "description": description,
                        "url": "https://www.co-drs.org/fr/jeu/capacites",
                    },
                )
                self.stdout.write(
                    self.style.SUCCESS(f"Created/updated cap {capability}")
                )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"Couldn't create/update cap {name}: {e}")
                )

    def get_paths(self, card: WebElement, name: str) -> list[Path]:
        paths = []
        try:
            for elem in card.find_elements(By.CSS_SELECTOR, ".card-back .paths a"):
                path_name = elem.text.replace("’", "'").strip()
                paths.append(Path.objects.get(name__iexact=path_name))
        except Exception:
            self.stdout.write(
                self.style.WARNING(f"Couldn't find path in card for cap '{name}'.")
            )
            return []
        return paths

    def setup_selenium(self):
        options = webdriver.FirefoxOptions()
        options.add_argument("-headless")
        self.selenium = webdriver.Firefox(options=options)
