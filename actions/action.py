from __future__ import annotations

import threading

from pathlib import Path

from gi.repository import Adw, Gtk
from loguru import logger as log

from src.backend.PluginManager.ActionBase import ActionBase


categories = Gtk.StringList.new(["MainCommand", "Emote"])


class DoAction(ActionBase):
    def __init__(self, *args, **kwargs) -> None:
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
        icon_path = self.cache_dir / category / f"{name}.png"
        if icon_path.exists():
            self.set_media(media_path=icon_path)
        else:
            log.debug(f"Cannot find {icon_path}")
            icon_path = Path(self.plugin_base.PATH) / "assets" / "info.png"
            self.set_media(media_path=icon_path)

        self.set_label(text=name.title())

    def get_config_rows(self) -> list[Adw.PreferencesRow]:
        self._action = Adw.EntryRow(title="Action Name")
        self._action.set_text(self.name)
        self._category = Adw.ComboRow(model=categories, title="Category")
        self._category.set_selected(self.category)

        # Connect signals
        self._action.connect("notify::text", self.on_action_changed)
        self._category.connect("notify::selected", self.on_category_changed)

        return [self._category, self._action]

    # Callbacks
    def on_ready(self) -> None:
        category = categories.get_string(self.category)
        self.update_appearance(category, self.name)

    def on_action_changed(self, entry: Adw.EntryRow) -> None:
        name = entry.get_text()

        settings = self.get_settings()
        settings["name"] = name
        self.set_settings(settings)

        category = categories.get_string(self.category)
        self.update_appearance(category, name)

    def on_category_changed(self, entry: Adw.ComboRow) -> None:
        category = entry.get_selected()

        settings = self.get_settings()
        settings["category"] = category
        self.set_settings(settings)

    def on_key_down(self) -> None:
        threading.Thread(
            target=self._on_key_down,
            daemon=True,
            name="get_request",
        ).start()

    def _on_key_down(self) -> None:
        action = self.name
        category = categories.get_string(self.category)

        # Find available actions
        actions = self.plugin_base.backend.get_json(f"action/{category}")
        action_data = None
        if actions is not None:
            for action_data in actions:
                if action_data.get("name") == action:
                    break
            else:
                action_data = None

        if action_data is None:
            log.error(f"Could not find action {action}")
            self.show_error(duration=1)
            return

        self.plugin_base.backend.post(f"action/{category}/{action_data['id']}/execute")
