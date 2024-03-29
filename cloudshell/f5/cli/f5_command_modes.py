from __future__ import annotations

import re
import time
from collections import OrderedDict
from typing import TYPE_CHECKING

from cloudshell.cli.service.command_mode import CommandMode

if TYPE_CHECKING:
    from typing import List


class EnableCommandMode(CommandMode):
    PROMPT = r"(?:(?!\)).)#\s*$"
    ENTER_COMMAND = "enable"
    EXIT_COMMAND = ""

    def __init__(self, resource_config):
        self.resource_config = resource_config
        super(EnableCommandMode, self).__init__(
            prompt=self.PROMPT,
            enter_command=self.ENTER_COMMAND,
            exit_command=self.EXIT_COMMAND,
            enter_action_map=self.enter_action_map(),
            exit_action_map=self.exit_action_map(),
            enter_error_map=self.enter_error_map(),
            exit_error_map=self.exit_error_map(),
        )

    def enter_action_map(self):
        return {
            "[Pp]assword": lambda session, logger: session.send_line(
                self.resource_config.enable_password, logger
            )
        }

    def enter_error_map(self):
        return OrderedDict()

    def exit_action_map(self):
        return OrderedDict()

    def exit_error_map(self):
        return OrderedDict()


class ConfigCommandMode(CommandMode):
    MAX_ENTER_CONFIG_MODE_RETRIES = 5
    ENTER_CONFIG_RETRY_TIMEOUT = 5
    PROMPT = r"\(tmos.*\)#\s*$"
    ENTER_COMMAND = "tmsh"
    EXIT_COMMAND = "quit"
    ENTER_ACTION_COMMANDS: List[str] = []

    def __init__(self, resource_config):
        self.resource_config = resource_config

        super(ConfigCommandMode, self).__init__(
            ConfigCommandMode.PROMPT,
            ConfigCommandMode.ENTER_COMMAND,
            ConfigCommandMode.EXIT_COMMAND,
            enter_action_map=self.enter_action_map(),
            exit_action_map=self.exit_action_map(),
            enter_error_map=self.enter_error_map(),
            exit_error_map=self.exit_error_map(),
        )

    def enter_action_map(self):
        return {r"{}.*$".format(EnableCommandMode.PROMPT): self._check_config_mode}

    def enter_error_map(self):
        return OrderedDict()

    def exit_error_map(self):
        return OrderedDict()

    def exit_action_map(self):
        return {self.PROMPT: lambda session, logger: session.send_line("quit", logger)}

    def enter_actions(self, cli_service):
        for cmd in self.ENTER_ACTION_COMMANDS:
            cli_service.send_command(cmd)

    def _check_config_mode(self, session, logger):
        error_message = "Failed to enter config mode, please check logs, for details"
        output = session.hardware_expect(
            "",
            expected_string="{0}|{1}".format(
                EnableCommandMode.PROMPT, ConfigCommandMode.PROMPT
            ),
            logger=logger,
        )
        retry = 0
        while (
            not re.search(ConfigCommandMode.PROMPT, output)
        ) and retry < self.MAX_ENTER_CONFIG_MODE_RETRIES:
            output = session.hardware_expect(
                ConfigCommandMode.ENTER_COMMAND,
                expected_string="{0}|{1}".format(
                    EnableCommandMode.PROMPT, ConfigCommandMode.PROMPT
                ),
                logger=logger,
            )
            time.sleep(self.ENTER_CONFIG_RETRY_TIMEOUT)
            retry += 1
        if not re.search(ConfigCommandMode.PROMPT, output):
            raise Exception(error_message)


CommandMode.RELATIONS_DICT = {EnableCommandMode: {ConfigCommandMode: {}}}
