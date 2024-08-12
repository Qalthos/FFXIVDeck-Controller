from __future__ import annotations

import os

from loguru import logger as log

from src.backend.DeckManagement.InputIdentifier import Input
from src.backend.PluginManager.ActionHolder import ActionHolder
from src.backend.PluginManager.ActionInputSupport import ActionInputSupport
from src.backend.PluginManager.PluginBase import PluginBase

from .actions.action import DoAction
from .actions.command import RunCommand
from .actions.job import ChangeClass
from .actions.volume import ChangeVolume


class FFXIVPlugin(PluginBase):
    def __init__(self) -> None:
        super().__init__()

        log.debug("Launch backend")
        backend = os.path.join(self.PATH, "backend", "backend.py")
        self.launch_backend(backend)

        ## Register actions
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

        self.command_holder = ActionHolder(
            plugin_base=self,
            action_base=RunCommand,
            action_id_suffix="RunCommand",
            action_name="Run Command",
            action_support={
                Input.Key: ActionInputSupport.SUPPORTED,
                Input.Dial: ActionInputSupport.UNSUPPORTED,
                Input.Touchscreen: ActionInputSupport.UNSUPPORTED,
            },
        )
        self.add_action_holder(self.command_holder)

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

        self.volume_holder = ActionHolder(
            plugin_base=self,
            action_base=ChangeVolume,
            action_id_suffix="ChangeVolume",
            action_name="Change Volume",
            action_support={
                Input.Key: ActionInputSupport.SUPPORTED,
                Input.Dial: ActionInputSupport.UNSUPPORTED,
                Input.Touchscreen: ActionInputSupport.UNSUPPORTED,
            },
        )
        self.add_action_holder(self.volume_holder)

        # Register plugin
        self.register(
            plugin_name="FFXIVDeck-Controller",
            github_repo="https://github.com/qalthos/FFXIVDeck-Controller",
            plugin_version="0.0.1",
            app_version="1.1.1-alpha",
        )
