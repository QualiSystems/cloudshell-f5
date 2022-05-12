# from cloudshell.devices.flows.snmp_action_flows import AutoloadFlow


# class AbstractF5SnmpAutoloadFlow(AutoloadFlow):
#     def execute_flow(self, supported_os, shell_name, shell_type, resource_name):
#         raise NotImplementedError(
#             "Class {} must implement method 'execute_flow'".format(type(self))
#         )


import re
from cloudshell.shell.flows.autoload.basic_flow import AbstractAutoloadFlow
# from cloudshell.networking.juniper.autoload.junos_snmp_autoload import JunosSnmpAutoload
# from cloudshell.f5.autoload.f5_generic_snmp_autoload import AbstractF5GenericSNMPAutoload
from cloudshell.f5.autoload.f5_generic_snmp_autoload import F5FirewallGenericSNMPAutoload
# from cloudshell.f5.autoload.f5_generic_snmp_autoload_bak import F5FirewallGenericSNMPAutoload


class BigIPAutoloadFlow(AbstractAutoloadFlow):
    def __init__(self, snmp_configurator, logger):
        """Autoload flow.

        :param cloudshell.snmp.snmp_configurator.
        EnableDisableSnmpConfigurator snmp_configurator:
        :param logging.Logger logger:
        """
        super(BigIPAutoloadFlow, self).__init__(logger)
        self._snmp_configurator = snmp_configurator

    # def _log_device_details(self, autoload_details):
    #     """Logging autoload details.
    #
    #     :param autoload_details:
    #     :return:
    #     """
    #     self._logger.debug("-------------------- <RESOURCES> ----------------------")
    #     for resource in autoload_details.resources:
    #         self._logger.debug(
    #             "{0:15}, {1:20}, {2}".format(
    #                 str(resource.relative_address),
    #                 resource.name,
    #                 resource.unique_identifier,
    #             )
    #         )
    #     self._logger.debug("-------------------- </RESOURCES> ----------------------")
    #
    #     self._logger.debug("-------------------- <ATTRIBUTES> ---------------------")
    #     for attribute in autoload_details.attributes:
    #         self._logger.debug(
    #             "-- {0:15}, {1:60}, {2}".format(
    #                 str(attribute.relative_address),
    #                 attribute.attribute_name,
    #                 attribute.attribute_value,
    #             )
    #         )
    #     self._logger.debug("-------------------- </ATTRIBUTES> ---------------------")

    # def _is_valid_device_os(self, supported_os, device_info):
    #     """Validate device OS using snmp.
    #
    #     :return: True or False
    #     """
    #     self._logger.debug("Detected system description: '{0}'".format(device_info))
    #     result = re.search(
    #         r"({0})".format("|".join(supported_os)),
    #         device_info,
    #         flags=re.DOTALL | re.IGNORECASE,
    #     )
    #
    #     if result:
    #         return True
    #     else:
    #         error_message = (
    #             "Incompatible driver! Please use this driver "
    #             "for '{0}' operation system(s)".format(str(tuple(supported_os)))
    #         )
    #         self._logger.error(error_message)
    #         return False

    # opt 1
    # def _autoload_flow(self, supported_os, resource_model):
    #     """Autoload Flow.
    #
    #     :param supported_os:
    #     :param cloudshell.shell.standards.networking.autoload_model.NetworkingResourceModel|cloudshell.shell.standards.firewall.autoload_model.FirewallResourceModel resource_model:  # noqa: E501
    #     :return:
    #     """
    #     with self._snmp_configurator.get_service() as snmp_service:
    #         snmp_autoload = JunosSnmpAutoload(snmp_service, self._logger)
    #         # snmp_autoload = JunosSnmpAutoload(snmp_service, self._logger)
    #         if not self._is_valid_device_os(supported_os, snmp_autoload.device_info):
    #             raise Exception(self.__class__.__name__, "Unsupported device OS")
    #
    #         snmp_autoload.build_root(resource_model)
    #         chassis_table = snmp_autoload.build_chassis(resource_model)
    #         snmp_autoload.build_power_modules(resource_model, chassis_table)
    #         module_table = snmp_autoload.build_modules(resource_model, chassis_table)
    #         sub_module_table = snmp_autoload.build_sub_modules(
    #             resource_model, module_table
    #         )
    #         snmp_autoload.build_ports(
    #             resource_model, chassis_table, module_table, sub_module_table
    #         )
    #         autoload_details = resource_model.build(filter_empty_modules=True)
    #     return autoload_details

    # # opt 2
    # def _autoload_flow(self, supported_os, resource_model):
    #     with self._snmp_handler.get_service() as snmp_service:
    #         snmp_service.add_mib_folder_path(self.MIBS_FOLDER)
    #         snmp_service.load_mib_tables(
    #             [
    #                 "PAN-COMMON-MIB",
    #                 "PAN-GLOBAL-REG",
    #                 "PAN-GLOBAL-TC",
    #                 "PAN-PRODUCTS-MIB",
    #                 "PAN-ENTITY-EXT-MIB",
    #             ]
    #         )
    #         snmp_autoload = PanOSGenericSNMPAutoload(snmp_service, self._logger)
    #
    #         snmp_autoload.if_table_service.PORT_CHANNEL_NAME = ["ae"]
    #         return snmp_autoload.discover(
    #             supported_os, resource_model, validate_module_id_by_port_name=False
    #         )

    # opt 3
    # def execute_flow(self, supported_os, shell_name, shell_type, resource_name):
    # def _autoload_flow(self, supported_os, shell_name, shell_type, resource_name):
    def _autoload_flow(self, supported_os, resource_model):
        # with self._snmp_handler.get_snmp_service() as snmp_service:
        # with self._snmp_configurator.get_snmp_service() as snmp_service:
        with self._snmp_configurator.get_service() as snmp_service:
            f5_snmp_autoload = F5FirewallGenericSNMPAutoload(
                snmp_service, self._logger
            )
            return f5_snmp_autoload.discover(supported_os, resource_model)
