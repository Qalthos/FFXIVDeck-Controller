from pathlib import Path
import json

from loguru import logger as log
import requests

from src.backend.PluginManager.ActionBase import ActionBase


class FFXIVDeckBase(ActionBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.base_uri = "http://127.0.0.1:37984"
        self.path = ""
        self.api_key = "Nn/gDBv9ljM13jJMpGXdr+G7L8HFc7KH"
        self.session = requests.Session()
        self.session.headers.update({"Authorization": f"Bearer {self.api_key}"})
        self.cache_dir = Path.home() / ".cache" / "ffxivdeck" / "icons"

    def post(self, path: str) -> str:
        try:
            response = self.session.post(self.base_uri + self.path + path, timeout=2)
            return response.text
        except Exception as exc:
            log.error(exc)
            self.show_error(duration=1)
        return ""

    def get_json(self, path: str):
        try:
            response = self.session.get(self.base_uri + self.path + path, timeout=2)
            log.debug(response.text)
            try:
                data = response.json()
                return data
            except json.decoder.JSONDecodeError as exc:
                log.error(exc)
                self.show_error(duration=1)
        except Exception as exc:
            log.error(exc)
            self.show_error(duration=1)
        return None
