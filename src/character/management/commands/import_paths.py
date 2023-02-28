from django.core.management import BaseCommand
from selenium import webdriver
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By

from character.models import Path, Profile, Race


class Command(BaseCommand):
    def handle(self, *args, **options) -> None:  # noqa: ARG002
        url = "https://www.co-drs.org/fr/jeu/voies"
        self.setup_selenium()
        self.selenium.get(url)
        anchors = []
        expected_path_count = 95
        while len(anchors) < expected_path_count:
            self.selenium.find_element(By.TAG_NAME, "body").send_keys(Keys.END)
            anchors = self.selenium.find_elements(
                By.CSS_SELECTOR,
                ".card-body .card-title a",
            )
        urls = [anchor.get_attribute("href") for anchor in anchors]
        for url in urls:
            try:
                self.import_path(url)
            except Exception as e:
                self.stderr.write(f"{type(e)}: {e}")
        self.stdout.write(f"Finished processing {len(urls)} paths.")

    def import_path(self, url: str):
        self.selenium.get(url)
        name = self.selenium.find_element(By.TAG_NAME, "h1").text.replace("’", "'")
        if name == "Voie du haut-elfe":  # Fix for incorrect data
            category = Path.Category.RACE
        else:
            category = self.get_category(name)
        profile = None
        if category == Path.Category.PROFILE:
            profile = self.get_profile(name)
        race = None
        if category == Path.Category.RACE:
            race = self.get_race(name)
        notes = self.get_notes()

        path, _ = Path.objects.update_or_create(
            name=name,
            defaults={
                "category": category,
                "profile": profile,
                "race": race,
                "notes": notes,
                "url": url,
            },
        )
        self.stdout.write(self.style.SUCCESS(f"Created/updated path {path}"))

    def get_category(self, name: str) -> Path.Category | None:
        try:
            category = (
                self.selenium.find_element(
                    By.CSS_SELECTOR,
                    ".field--name-type .field__item",
                )
                .text.lower()
                .strip()
            )
        except Exception:
            self.stdout.write(
                self.style.WARNING(
                    f"Couldn't find category for {name}. Defaulting to profile.",
                ),
            )
            return Path.Category.PROFILE

        if category == "personnage":
            return Path.Category.PROFILE
        if category == "créature":
            return Path.Category.CREATURE
        return Path.Category(category)

    def get_profile(self, name: str) -> Profile | None:
        try:
            profile_name = self.selenium.find_element(
                By.CSS_SELECTOR,
                ".field--name-type + strong + a",
            ).text
        except Exception:
            self.stdout.write(self.style.WARNING(f"Couldn't find profile for {name}"))
        else:
            return Profile.objects.get_by_natural_key(profile_name)

    def get_race(self, path_name: str) -> Race | None:
        to_remove = ["voie de la", "voie de l'", "voie du"]
        path_name = path_name.lower()
        for text in to_remove:
            path_name = path_name.replace(text, "")
        try:
            return Race.objects.get(name__iexact=path_name.strip())
        except Exception:
            self.stdout.write(self.style.WARNING(f"Couldn't find race for {path_name}"))

    def get_notes(self) -> str:
        try:
            return self.selenium.find_element(
                By.CSS_SELECTOR,
                ".mt-3 > .field--name-description",
            ).text.strip()
        except Exception:
            return ""

    def setup_selenium(self):
        options = webdriver.FirefoxOptions()
        options.add_argument("-headless")
        self.selenium = webdriver.Firefox(options=options)
