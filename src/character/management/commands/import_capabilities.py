from django.core.management import BaseCommand
from selenium import webdriver
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

from character.models import Capability, Path


class Command(BaseCommand):
    def handle(self, *args, **options):
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
                print(f"{type(e)}: {e}")
        self.stdout.write(f"Finished processing {len(cards)} caps.")

    def import_capability(self, card: WebElement):
        title = (
            card.find_element(By.CSS_SELECTOR, ".card-front .card-title .fw-bold")
            .text.strip()
            .split(" | ")
        )
        name = title[0].replace("’", "'").strip()
        rank = int(title[1].replace("rang ", ""))
        path = self.get_path(card, name)
        limited = False
        if "(L)" in name:
            limited = True
            name = name.replace("(L)", "")
        spell = False
        if "*" in name:
            spell = True
            name = name.replace("*", "")
        name = name.strip()
        try:
            capability, _ = Capability.objects.update_or_create(
                name=name,
                defaults={
                    "rank": rank,
                    "path": path,
                    "limited": limited,
                    "spell": spell,
                },
            )
            self.stdout.write(self.style.SUCCESS(f"Created/updated cap {capability}"))
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"Couldn't create/update cap {name}: {e}")
            )

    def get_path(self, card: WebElement, name: str) -> Path | None:
        try:
            path_name = (
                card.find_element(By.CSS_SELECTOR, ".card-back .paths a")
                .text.replace("’", "'")
                .strip()
            )
        except Exception:
            self.stdout.write(
                self.style.WARNING(f"Couldn't find path in card for cap '{name}'.")
            )
            return None
        try:
            path = Path.objects.get(name__iexact=path_name)
            return path
        except Exception:
            self.stdout.write(
                self.style.WARNING(
                    f"Couldn't find path name '{path_name}' for cap '{name}'."
                )
            )
            return None

    def setup_selenium(self):
        options = webdriver.FirefoxOptions()
        options.add_argument("-headless")
        self.selenium = webdriver.Firefox(options=options)
