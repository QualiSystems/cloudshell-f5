from __future__ import annotations

import os
from typing import TYPE_CHECKING

from cloudshell.shell.core.driver_context import AutoLoadDetails
from cloudshell.shell.flows.autoload.basic_flow import AbstractAutoloadFlow

from cloudshell.f5.autoload.f5_generic_snmp_autoload import (
    F5FirewallGenericSNMPAutoload,
)

if TYPE_CHECKING:
    from logging import Logger

    from cloudshell.shell.standards.networking.autoload_model import (
        NetworkingResourceModel,
    )
    from cloudshell.snmp.snmp_configurator import EnableDisableSnmpConfigurator


class BigIPAutoloadFlow(AbstractAutoloadFlow):
    def __init__(
        self,
        snmp_configurator: EnableDisableSnmpConfigurator,
        logger: Logger,
    ):
        super(BigIPAutoloadFlow, self).__init__(logger)
        self._snmp_configurator = snmp_configurator

    def _autoload_flow(
        self, supported_os: list[str], resource_model: NetworkingResourceModel
    ) -> AutoLoadDetails:
        with self._snmp_configurator.get_service() as snmp_service:
            snmp_service.add_mib_folder_path(
                os.path.join(os.path.dirname(__file__), "..", "snmp", "mibs")
            )
            f5_snmp_autoload = F5FirewallGenericSNMPAutoload(snmp_service, self._logger)

            return f5_snmp_autoload.discover(supported_os, resource_model)
