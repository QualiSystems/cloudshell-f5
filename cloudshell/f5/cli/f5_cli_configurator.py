#!/usr/bin/python
# -*- coding: utf-8 -*-

from cloudshell.cli.configurator import AbstractModeConfigurator
from cloudshell.cli.service.command_mode_helper import CommandModeHelper

# todo clean comments in this file
from cloudshell.f5.cli.f5_command_modes import (
    ConfigCommandMode,
    EnableCommandMode,  # todo needed? theres no default mode
    # DefaultCommandMode,
)
# from cloudshell.networking.juniper.cli.juniper_ssh_session import JuniperSSHSession
from cloudshell.f5.cli.f5_ssh_session import F5SSHSession

# from cloudshell.networking.juniper.cli.juniper_telnet_session import (
#     JuniperTelnetSession,
# )
from cloudshell.f5.cli.f5_telnet_session import F5TelnetSession


class F5CliConfigurator(AbstractModeConfigurator):
    REGISTERED_SESSIONS = (F5SSHSession, F5TelnetSession)
    # REGISTERED_SESSIONS = (JuniperSSHSession, JuniperTelnetSession)

    def __init__(self, cli, resource_config, logger):
        super(F5CliConfigurator, self).__init__(resource_config, logger, cli)
        self.modes = CommandModeHelper.create_command_mode(resource_config)

    @property
    def enable_mode(self):
        return self.modes.get(EnableCommandMode)
        # return self.modes.get(DefaultCommandMode)

    @property
    def config_mode(self):
        return self.modes.get(ConfigCommandMode)
