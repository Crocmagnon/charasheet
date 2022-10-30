from django.core.management import BaseCommand
from selenium import webdriver
from selenium.webdriver.common.by import By

from character.models import Race


class Command(BaseCommand):
    def handle(self, *args, **options) -> None:
        url = "https://www.co-drs.org/fr/jeu/races"
        self.setup_selenium()
        self.selenium.get(url)
        anchors = self.selenium.find_elements(By.CSS_SELECTOR, "h2 a")
        urls = [anchor.get_attribute("href") for anchor in anchors]
        for url in urls:
            try:
                self.import_race(url)
            except Exception as e:
                print(f"{type(e)}: {e}")
        self.stdout.write(f"Finished processing {len(urls)} races.")

    def import_race(self, url: str) -> None:
        self.selenium.get(url)
        name = self.selenium.find_element(By.TAG_NAME, "h1").text.strip()
        name = self.fix_name(name)
        race, _ = Race.objects.update_or_create(name=name, defaults={"url": url})
        self.stdout.write(self.style.SUCCESS(f"Created/updated race {race}"))

    def fix_name(self, name: str) -> str:
        if name == "Elfe, haut":
            return "Haut-Elfe"
        if name == "Elfe, sylvain":
            return "Elfe Sylvain"
        return name

    def setup_selenium(self) -> None:
        options = webdriver.FirefoxOptions()
        options.add_argument("-headless")
        self.selenium = webdriver.Firefox(options=options)
