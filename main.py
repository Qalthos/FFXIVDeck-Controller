from loguru import log

from src.backend.DeckManagement.InputIdentifier import Input
from src.backend.PluginManager.ActionHolder import ActionHolder
from src.backend.PluginManager.ActionInputSupport import ActionInputSupport
from src.backend.PluginManager.PluginBase import PluginBase
from .actions.action import DoAction
from .actions.job import ChangeClass


class FFXIVPlugin(PluginBase):
    def __init__(self):
        super().__init__()

        log.debug("Launch backend")

        ## Register actions
        self.job_holder = ActionHolder(
            plugin_base=self,
            action_base=ChangeClass,
            action_id_suffix="ChangeClass",
            action_name="Change Class",
            action_support={
                Input.Key: ActionInputSupport.SUPPORTED,
                Input.Dial: ActionInputSupport.UNSUPPORTED,
                Input.Touchscreen: ActionInputSupport.UNSUPPORTED,
            },
        )
        self.add_action_holder(self.job_holder)

        self.action_holder = ActionHolder(
            plugin_base=self,
            action_base=DoAction,
            action_id_suffix="DoAction",
            action_name="Do Action",
            action_support={
                Input.Key: ActionInputSupport.SUPPORTED,
                Input.Dial: ActionInputSupport.UNSUPPORTED,
                Input.Touchscreen: ActionInputSupport.UNSUPPORTED,
            },
        )
        self.add_action_holder(self.action_holder)

        # Register plugin
        self.register(
            plugin_name="FFXIVDeck-Controller",
            github_repo="https://github.com/qalthos/FFXIVDeck-Controller",
            plugin_version="0.0.1",
            app_version="1.0.0-alpha"
        )
