#!/usr/bin/python
# -*- coding: utf-8 -*-

from cloudshell.cli.configurator import AbstractModeConfigurator
from cloudshell.cli.service.command_mode_helper import CommandModeHelper

from cloudshell.f5.cli.f5_command_modes import ConfigCommandMode, EnableCommandMode
from cloudshell.f5.cli.f5_ssh_session import F5SSHSession
from cloudshell.f5.cli.f5_telnet_session import F5TelnetSession


class F5CliConfigurator(AbstractModeConfigurator):
    REGISTERED_SESSIONS = (F5SSHSession, F5TelnetSession)

    def __init__(self, cli, resource_config, logger):
        super(F5CliConfigurator, self).__init__(resource_config, logger, cli)
        self.modes = CommandModeHelper.create_command_mode(resource_config)

    @property
    def enable_mode(self):
        return self.modes.get(EnableCommandMode)

    @property
    def config_mode(self):
        return self.modes.get(ConfigCommandMode)
