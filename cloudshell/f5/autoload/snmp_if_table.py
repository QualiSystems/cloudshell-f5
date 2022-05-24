from cloudshell.snmp.autoload.snmp_if_table import SnmpIfTable


class F5SnmpIfTable(SnmpIfTable):
    PORT_EXCLUDE_LIST = ["mgmt", "management", "loopback", "null"]

    def _get_if_entities(self):
        for port in self._if_table:
            # commented default logic piece due to dot (.) being legal for f5
            # if "." in port.safe_value:
            #     continue
            if any(
                port_channel
                for port_channel in self.PORT_CHANNEL_NAME
                if port_channel in port.safe_value.lower()
            ):
                self._add_port_channel(port)
            elif not any(
                exclude_port
                for exclude_port in self.port_exclude_list
                if exclude_port in port.safe_value.lower()
            ):
                self._add_port(port)
