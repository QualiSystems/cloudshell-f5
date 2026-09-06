from __future__ import annotations

from cloudshell.snmp.autoload.generic_snmp_autoload import GenericSNMPAutoload

from cloudshell.f5.autoload.f5_ports_table import F5PortsTable


class F5FirewallGenericSNMPAutoload(GenericSNMPAutoload):
    _port_table_service: F5PortsTable | None

    @property
    def port_table_service(self) -> F5PortsTable:
        if not self._port_table_service:
            self._port_table_service = F5PortsTable(
                resource_model=self._resource_model,
                ports_snmp_table=self.port_snmp_table,
                logger=self.logger,
            )
        return self._port_table_service
