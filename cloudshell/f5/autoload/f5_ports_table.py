from cloudshell.snmp.autoload.services.port_table import PortsTable


class F5PortsTable(PortsTable):
    # dot (.) is legal in F5 port names, so it is not excluded here
    PORT_EXCLUDE_LIST = [r"mgmt|management|loopback|null"]
