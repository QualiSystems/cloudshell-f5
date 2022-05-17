
from cloudshell.shell.flows.autoload.basic_flow import AbstractAutoloadFlow

from cloudshell.f5.autoload.f5_generic_snmp_autoload import (
    F5FirewallGenericSNMPAutoload,
)


class BigIPAutoloadFlow(AbstractAutoloadFlow):
    def __init__(self, snmp_configurator, logger):
        """Autoload flow.

        :param cloudshell.snmp.snmp_configurator.
        EnableDisableSnmpConfigurator snmp_configurator:
        :param logging.Logger logger:
        """
        super(BigIPAutoloadFlow, self).__init__(logger)
        self._snmp_configurator = snmp_configurator

    def _autoload_flow(self, supported_os, resource_model):
        with self._snmp_configurator.get_service() as snmp_service:
            f5_snmp_autoload = F5FirewallGenericSNMPAutoload(
                snmp_service, self._logger
            )
            return f5_snmp_autoload.discover(supported_os, resource_model)
