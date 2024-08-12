from __future__ import annotations

import json
import threading

from pathlib import Path

from gi.repository import Adw

from src.backend.PluginManager.ActionBase import ActionBase


class RunCommand(ActionBase):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    @property
    def command(self) -> str:
        settings = self.get_settings()
        return settings.get("command", "")

    def get_config_rows(self) -> list:
        self._command = Adw.EntryRow(title="Command to run")
        self._command.set_text(self.command)

        # Connect signals
        self._command.connect("notify::text", self.on_command_changed)

        return [self._command]

    # Callbacks
    def on_ready(self) -> None:
        icon_path = Path(self.plugin_base.PATH) / "assets" / "info.png"
        self.set_media(media_path=icon_path)

    def on_command_changed(self, entry: Adw.EntryRow) -> None:
        command = entry.get_text()

        settings = self.get_settings()
        settings["command"] = command
        self.set_settings(settings)

    def on_key_down(self) -> None:
        threading.Thread(
            target=self._on_key_down,
            daemon=True,
            name="get_request",
        ).start()

    def _on_key_down(self) -> None:
        payload = {"command": self.command}
        data = json.dumps(payload)

        self.plugin_base.backend.post("command", data=data)
