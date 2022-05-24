# #!/usr/bin/python
# # -*- coding: utf-8 -*-
#
from cloudshell.snmp.autoload.generic_snmp_autoload import GenericSNMPAutoload

from cloudshell.f5.autoload.snmp_if_table import F5SnmpIfTable


class F5FirewallGenericSNMPAutoload(GenericSNMPAutoload):
    @property
    def if_table_service(self):
        if not self._if_table:
            self._if_table = F5SnmpIfTable(
                snmp_handler=self.snmp_handler, logger=self.logger
            )

        return self._if_table
