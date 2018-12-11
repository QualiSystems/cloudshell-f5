from cloudshell.devices.runners.autoload_runner import AutoloadRunner


class AbstractF5AutoloadRunner(AutoloadRunner):
    def __init__(self, logger, resource_config, snmp_handler):
        super(AbstractF5AutoloadRunner, self).__init__(resource_config)
        self._logger = logger
        self.snmp_handler = snmp_handler

    @property
    def autoload_flow(self):
        raise NotImplementedError("Class {} must implement property 'autoload_flow'".format(type(self)))
