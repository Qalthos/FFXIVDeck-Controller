import os
import sys


from src.backend.PluginManager.PluginBase import PluginBase
from src.backend.PluginManager.ActionHolder import ActionHolder
from src.backend.DeckManagement.InputIdentifier import Input
from src.backend.PluginManager.ActionInputSupport import ActionInputSupport
from plugins.com_linkybook_ffxivdeck.actions import jobs, action

# Import gtk modules
import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk

# Add plugin to sys.paths
sys.path.append(os.path.dirname(__file__))


class FFXIVPlugin(PluginBase):
    def __init__(self):
        super().__init__()

        self.init_locale_manager()

        self.lm = self.locale_manager

        ## Register actions
        self.job_holder = ActionHolder(
            plugin_base=self,
            action_base=jobs.ChangeJob,
            action_id_suffix="ChangeJob",
            action_name="Change Job",
            icon=Gtk.Picture.new_for_filename(os.path.join(self.PATH, "assets", "job.webp")),
            action_support={
                Input.Key: ActionInputSupport.SUPPORTED,
                Input.Dial: ActionInputSupport.UNTESTED,
                Input.Touchscreen: ActionInputSupport.UNTESTED
            }
        )
        self.add_action_holder(self.job_holder)

        self.action_holder = ActionHolder(
            plugin_base=self,
            action_base=action.DoAction,
            action_id_suffix="DoAction",
            action_name="DO Action",
            icon=Gtk.Picture.new_for_filename(os.path.join(self.PATH, "assets", "job.webp")),
            action_support={
                Input.Key: ActionInputSupport.SUPPORTED,
                Input.Dial: ActionInputSupport.UNTESTED,
                Input.Touchscreen: ActionInputSupport.UNTESTED
            }
        )
        self.add_action_holder(self.action_holder)

        # Register plugin
        self.register(
            plugin_name=self.lm.get("plugin.name"),
            github_repo="https://github.com/qalthos/FFXIVDeck-Controller",
            plugin_version="1.0.0",
            app_version="1.0.0-alpha"
        )

    def init_locale_manager(self):
        self.lm = self.locale_manager
        self.lm.set_to_os_default()

    def get_selector_icon(self) -> Gtk.Widget:
        return Gtk.Image(icon_name="network-transmit-receive")
