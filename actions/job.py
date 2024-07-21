import os
import threading

# Import gtk modules - used for the config rows
import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw
from loguru import logger as log

from plugins.com_linkybook_FFXIVDeck.actions import FFXIVDeckBase


class ChangeClass(FFXIVDeckBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.path = "/classes"
        self.cache_dir /= "class"

    def on_ready(self):
        icon_path = os.path.join(self.plugin_base.PATH, "assets", "info.png")
        self.set_media(media_path=icon_path)

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
