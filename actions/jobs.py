import os
import threading

from gi.repository import Adw
from loguru import logger as log

from plugins.com_linkybook_ffxivdeck.actions import FFXIVDeckBase


class ChangeJob(FFXIVDeckBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.path = "/classes"
        self.cache_dir /= "class"

    def on_ready(self):
        self.set_media(media_path=os.path.join(self.plugin_base.PATH, "assets", "job.webp"), size=0.8)

    def get_config_rows(self) -> list:
        self.job_name = Adw.EntryRow(title="Job Name")

        self.load_config_defaults()

        # Connect signals
        self.job_name.connect("notify::text", self.on_job_changed)

        return [self.job_name]

    def on_job_changed(self, entry, *args):
        job_name = entry.get_text()

        settings = self.get_settings()
        settings["name"] = job_name
        self.set_settings(settings)

        # Appearance
        self.set_label(text=job_name.title())
        icon_path = self.cache_dir / f"{job_name.lower()}.png"
        if icon_path.exists():
            self.set_media(media_path=icon_path)
        else:
            log.debug(f"Cannot find {icon_path}")

    def load_config_defaults(self):
        settings = self.get_settings()
        self.job_name.set_text(settings.get("name", "")) # Does not accept None

    def on_key_down(self):
        threading.Thread(target=self._on_key_down, daemon=True, name="get_request").start()

    def _on_key_down(self):
        settings = self.get_settings()
        job = settings.get("name")

        # Find available classes
        classes = self.get_json("/available")
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

        self.post(f"/{class_data['id']}/execute")
