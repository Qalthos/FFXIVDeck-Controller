import os
from pathlib import Path
import threading

from gi.repository import Adw
from loguru import logger as log

from src.backend.PluginManager.ActionBase import ActionBase


class ChangeClass(ActionBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.cache_dir = Path("~/.cache").expanduser() / "ffxivdeck" / "class"

    @property
    def name(self) -> str:
        settings = self.get_settings()
        return settings.get("name", "")

    def on_ready(self) -> None:
        self.update_appearance(self.name)

    def update_appearance(self, job_name: str) -> None:
        icon_path = self.cache_dir / f"{job_name.lower()}.png"
        if icon_path.exists:
            self.set_media(media_path=icon_path)
        else:
            log.debug(f"Cannot find {icon_path}")
            icon_path = os.path.join(self.plugin_base.PATH, "assets", "info.png")
            self.set_media(media_path=icon_path)

        self.set_label(text=job_name.title())

    def get_config_rows(self) -> list[Adw.EntryRow]:
        self.job_name = Adw.EntryRow(title="Job Name")
        self.job_name.set_text(self.name)

        # Connect signals
        self.job_name.connect("notify::text", self.on_job_changed)

        return [self.job_name]

    def on_job_changed(self, entry, *args) -> None:
        job_name = entry.get_text()

        settings = self.get_settings()
        settings["name"] = job_name
        self.set_settings(settings)

        self.update_appearance(job_name)

    def on_key_down(self) -> None:
        threading.Thread(target=self._on_key_down, daemon=True, name="get_request").start()

    def _on_key_down(self) -> None:
        settings = self.get_settings()
        job = settings.get("name")

        # Find available classes
        try:
            classes = self.plugin_base.backend.get_json("classes/available")
        except Exception as exc:
            log.error(f"Could not communicate with backend: {exc}")
            self.show_error(duration=1)
            return

        class_data = None
        if classes is not None:
            for class_data in classes:
                if class_data.get("name") == job.lower():
                    break
            else:
                class_data = None

        if class_data is None:
            log.error(f"Could not find class {job}")
            self.show_error(duration=1)
            return

        self.plugin_base.backend.post(f"classes/{class_data['id']}/execute")
