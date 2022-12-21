import json


class Settings:
    def __init__(self, filename):
        with open(filename) as f:
            self.SETTINGS = json.load(f)

    def __getitem__(self, item):
        try:
            return self.SETTINGS[item]

        except KeyError as e:
            raise KeyError(f"Item {item} is not in settings") from e


settings = Settings("settings.json")
