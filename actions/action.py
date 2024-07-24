import os
from pathlib import Path
import threading

from gi.repository import Gtk, Adw
from loguru import logger as log

from src.backend.PluginManager.ActionBase import ActionBase


categories = Gtk.StringList.new(["MainCommand", "Emote"])


class DoAction(ActionBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.cache_dir = Path("~/.cache").expanduser() / "ffxivdeck" / "icons" / "action"

    @property
    def name(self) -> str:
        settings = self.get_settings()
        return settings.get("name", "")

    @property
    def category(self) -> int:
        settings = self.get_settings()
        return settings.get("category", 0)

    def update_appearance(self, category: str, name: str) -> None:
        icon_path = self.cache_dir / category / f"{name.lower()}.png"
        if icon_path.exists():
            self.set_media(media_path=icon_path)
        else:
            log.debug(f"Cannot find {icon_path}")
            icon_path = os.path.join(self.plugin_base.PATH, "assets", "info.png")
            self.set_media(media_path=icon_path)

        self.set_label(text=name.title())

    def get_config_rows(self) -> list:
        self._category = Adw.ComboRow(model=categories, title="Category")
        self._category.set_selected(self.category)
        self.action_name = Adw.EntryRow(title="Action Name")
        self.action_name.set_text(self.name)

        # Connect signals
        self.action_name.connect("notify::text", self.on_action_changed)

        return [self._category, self.action_name]

    # Callbacks
    def on_ready(self) -> None:
        category = categories.get_string(self.category)
        self.update_appearance(category, self.name)

    def on_action_changed(self, entry, *args):
        action_name = entry.get_text()

        settings = self.get_settings()
        settings["name"] = action_name
        self.set_settings(settings)

        self.update_appearance()

    def on_key_down(self):
        threading.Thread(target=self._on_key_down, daemon=True, name="get_request").start()

    def _on_key_down(self):
        action = self.action
        category = categories.get_string(self.category)

        # Find available actions
        actions = self.get_json(f"actions/{category}")
        action_data = None
        if actions is not None:
            for action_data in actions:
                if action_data.get("name") == action.lower():
                    break
            else:
                action_data = None

        if action_data is None:
            log.error(f"Could not find action {action}")
            self.show_error(duration=1)
            return

        self.post(f"actions/{action_data['id']}/execute")
