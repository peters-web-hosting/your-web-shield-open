from Database import Database


class CountryRisk:
    def __init__(self):
        self.known_bad = ["RU", "CN", "BR"]  # Added China and Brazil to the list

    def update_risk(self):
        db = Database()
        countries = db.getCountries()
        for country in countries:
            new_risk = db.countryRisk(country[0])
            if new_risk is None:
                new_risk = 0
            if country not in self.known_bad:
                new_risk += 6
            new_risk = min(new_risk, 99)
            print(new_risk, country[0])
            db.update_country_risk(country[0], new_risk)


if __name__ == "__main__":
    country_risk = CountryRisk()
    country_risk.update_risk()
