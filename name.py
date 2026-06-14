from faker import Faker

from country import Country

LOCALE_MAP = {
    Country.India: "en_IN",
    Country.Argentina: "es_AR",
    Country.Spain: "es_ES",
    Country.France: "fr_FR",
    Country.England: "en_GB",
    Country.Portugal: "pt_PT",
}


class Name:
    def __init__(self):
        self._firstName = ""
        self._lastName = ""

    @classmethod
    def generate(cls, country: Country) -> "Name":
        fake = Faker(LOCALE_MAP[country])
        obj = cls()
        obj._firstName = fake.first_name_male()
        obj._lastName = fake.last_name()
        return obj

    @property
    def firstName(self):
        return self._firstName

    @property
    def lastName(self):
        return self._lastName

    @property
    def fullName(self):
        return f"{self._firstName} {self._lastName}".strip()
