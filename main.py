from src.backend.PluginManager.PluginBase import PluginBase
from src.backend.PluginManager.ActionHolder import ActionHolder

# Import actions
from .actions.action import DoAction
from .actions.job import ChangeClass


class FFXIVPlugin(PluginBase):
    def __init__(self):
        super().__init__()

        ## Register actions
        self.job_holder = ActionHolder(
            plugin_base=self,
            action_base=ChangeClass,
            action_id_suffix="ChangeClass",
            action_name="Change Class",
        )
        self.add_action_holder(self.job_holder)

        self.action_holder = ActionHolder(
            plugin_base=self,
            action_base=DoAction,
            action_id_suffix="DoAction",
            action_name="Do Action",
        )
        self.add_action_holder(self.action_holder)

        # Register plugin
        self.register(
            plugin_name="FFXIVDeck-Controller",
            github_repo="https://github.com/qalthos/FFXIVDeck-Controller",
            plugin_version="0.0.1",
            app_version="1.0.0-alpha"
        )
