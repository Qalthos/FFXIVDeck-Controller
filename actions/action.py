import threading

# Import gtk modules - used for the config rows
import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw
from loguru import logger as log

from plugins.com_linkybook_FFXIVDeck.actions import FFXIVDeckBase


categories = Gtk.StringList()
# "MainCommand", "Emote")


class DoAction(FFXIVDeckBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.path = "/action"
        self.cache_dir /= "action"

    def on_ready(self):
        icon_path = os.path.join(self.plugin_base.PATH, "assets", "info.png")
        self.set_media(media_path=icon_path)
        self.update()

    def update(self):
        settings = self.get_settings()
        category = settings.get("category")
        action_name = settings.get("name")

        # Appearance
        self.set_label(text=action_name.title())
        icon_path = self.cache_dir / category / f"{action_name.lower()}.png"
        if icon_path.exists():
            self.set_media(media_path=icon_path)
        else:
            log.debug(f"Cannot find {icon_path}")

    def get_config_rows(self) -> list:
        self.category = Adw.ComboRow(model=categories, title="Category")
        self.name = Adw.EntryRow(title="Action Name")

        self.load_config_defaults()

        # Connect signals
        self.name.connect("notify::text", self.on_action_changed)

        return [self.category, self.name]

    def on_job_changed(self, entry, *args):
        action_name = entry.get_text()

        settings = self.get_settings()
        settings["name"] = action_name
        self.set_settings(settings)

        self.update()

    def load_config_defaults(self):
        settings = self.get_settings()
        self.category.set_text(settings.get("name", "")) # Does not accept None
        self.name.set_text(settings.get("name", "")) # Does not accept None

    def on_key_down(self):
        threading.Thread(target=self._on_key_down, daemon=True, name="get_request").start()

    def _on_key_down(self):
        settings = self.get_settings()
        category = settings.get("category")
        action_name = settings.get("name")

        # Find available classes
        actions = self.get_json(f"/{category}")
        action_data = None
        if actions is not None:
            for action_data in actions:
                if action_data.get("name") == action_name.lower():
                    break
            else:
                action_data = None

        if action_data is None:
            log.error(f"Could not find action {action_name}")
            self.show_error(duration=1)
            return

        self.post(f"/{action_data['id']}/execute")
