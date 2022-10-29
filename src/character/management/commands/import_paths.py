from django.core.management import BaseCommand
from selenium import webdriver
from selenium.webdriver.common.by import By

from character.models import Path, Profile, Race


class Command(BaseCommand):
    def handle(self, *args, **options):
        url = "https://www.co-drs.org/fr/jeu/voies"
        self.setup_selenium()
        self.selenium.get(url)
        anchors = self.selenium.find_elements(
            By.CSS_SELECTOR, ".card-body .card-title a"
        )
        urls = [anchor.get_attribute("href") for anchor in anchors]
        for url in urls:
            try:
                self.import_path(url)
            except Exception as e:
                print(f"{type(e)}: {e}")
        self.stdout.write(f"Finished processing {len(urls)} paths.")

    def import_path(self, url: str):
        self.selenium.get(url)
        name = self.selenium.find_element(By.TAG_NAME, "h1").text
        category = self.get_category(name)
        profile = None
        if category == Path.Category.PROFILE:
            profile = self.get_profile()
        race = None
        if category == Path.Category.RACE:
            profile = self.get_race(name)

        path, _ = Path.objects.update_or_create(
            name=name,
            defaults={"category": category, "profile": profile, "race": race},
        )
        self.stdout.write(self.style.SUCCESS(f"Created/updated path {path}"))

    def get_category(self, name: str) -> Path.Category | None:
        try:
            category = (
                self.selenium.find_element(
                    By.CSS_SELECTOR, ".field--name-type .field__item"
                )
                .text.lower()
                .strip()
            )
        except Exception:
            self.stdout.write(
                self.style.WARNING(
                    f"Couldn't find category for {name}. Defaulting to profile."
                )
            )
            return Path.Category.PROFILE

        if category == "personnage":
            return Path.Category.PROFILE
        if category == "créature":
            return Path.Category.CREATURE
        return Path.Category(category)

    def get_profile(self) -> Profile:
        profile_name = self.selenium.find_element(
            By.CSS_SELECTOR, ".field--name-type + strong + a"
        ).text
        return Profile.objects.get_by_natural_key(profile_name)

    def get_race(self, path_name: str) -> Race:
        return None
        to_remove = [""]
        for text in to_remove:
            path_name = path_name.replace(text, "")
        return Race.objects.get(name__iexact=path_name)

    def setup_selenium(self):
        options = webdriver.FirefoxOptions()
        options.add_argument("-headless")
        self.selenium = webdriver.Firefox(options=options)
