from cloudshell.devices.flows.snmp_action_flows import AutoloadFlow


class AbstractF5SnmpAutoloadFlow(AutoloadFlow):
    def execute_flow(self, supported_os, shell_name, shell_type, resource_name):
        raise NotImplementedError("Class {} must implement method 'execute_flow'".format(type(self)))
