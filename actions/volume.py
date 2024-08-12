from __future__ import annotations

import os
import threading

from typing import TYPE_CHECKING

from gi.repository import Adw

from src.backend.PluginManager.ActionBase import ActionBase


if TYPE_CHECKING:
    from .backend.message_types import VolumeOpcode, VolumePayload


class ChangeVolume(ActionBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @property
    def channel(self) -> str:
        settings = self.get_settings()
        return settings.get("channel", "")

    @property
    def value(self) -> int:
        settings = self.get_settings()
        return settings.get("value", 0)

    def get_config_rows(self) -> list:
        self._channel = Adw.EntryRow(title="Channel to control")
        self._channel.set_text(self.channel)

        self._value = Adw.EntryRow(title="Value to apply")
        self._value.set_text(self.value)

        # Connect signals
        self._channel.connect("notify::text", self.on_command_changed)
        self._value.connect("notify::text", self.on_value_changed)

        return [self._channel, self._value]

    # Callbacks
    def on_ready(self) -> None:
        icon_path = os.path.join(self.plugin_base.PATH, "assets", "info.png")
        self.set_media(media_path=icon_path)

    def on_channel_changed(self, entry, *args) -> None:
        channel = entry.get_text()

        settings = self.get_settings()
        settings["channel"] = channel
        self.set_settings(settings)

    def on_value_changed(self, entry, *args) -> None:
        value = int(entry.get_text())

        settings = self.get_settings()
        settings["value"] = value
        self.set_settings(settings)

    def on_key_down(self) -> None:
        threading.Thread(
            target=self._on_key_down,
            daemon=True,
            name="get_request",
        ).start()

    def _on_key_down(self) -> None:
        payload = volume_message(
            channel=self.channel,
            volume=self.value,
        )

        self.plugin_base.backend.ws_send(payload=payload)


def volume_message(
    channel="master",
    volume: int | None = None,
    delta: int | None = None,
    mute: bool | None = None,
) -> VolumeOpcode:

    data: VolumePayload = {}
    if volume is not None:
        data["Volume"] = volume
    if delta is not None:
        data["Delta"] = delta
    if mute is not None:
        data["Muted"] = mute

    volume_payload: VolumeOpcode = {
        "Opcode": "setVolume",
        "Channel": channel,
        "Data": data,
    }
    return volume_payload
