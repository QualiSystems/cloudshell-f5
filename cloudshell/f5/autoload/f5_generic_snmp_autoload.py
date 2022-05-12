#!/usr/bin/python
# -*- coding: utf-8 -*-

import re

from cloudshell.snmp.autoload.generic_snmp_autoload import GenericSNMPAutoload
# from cloudshell.snmp.autoload.generic_snmp_autoload import (
#     GeneralAutoloadError,
#     GenericSNMPAutoload,
#     SnmpEntityTable,
#     log_autoload_details,
# )


class F5FirewallGenericSNMPAutoload(GenericSNMPAutoload):
    # todo idk if something needs to be added here
    # todo probably snmp if table files have something in them
    pass
#
# class PanOSGenericSNMPAutoload(GenericSNMPAutoload):
#     def __init__(self, snmp_handler, logger):
#         super(PanOSGenericSNMPAutoload, self).__init__(snmp_handler, logger)
#         self._if_ports_in_entity = False
#         self._chassis = {}
#
#     @property
#     def system_info_service(self):
#         if not self._system_info:
#             self._system_info = PanOSSNMPSystemInfo(self.snmp_handler, self.logger)
#         return self._system_info
#
#     def discover(
#         self, supported_os, resource_model, validate_module_id_by_port_name=False
#     ):
#         """General entry point for autoload.
#
#         Read device structure and attributes: chassis, modules, submodules, ports,
#         port-channels and power supplies
#         :type resource_model: cloudshell.shell.standards.autoload_generic_models.GenericResourceModel  # noqa: E501
#         :param str supported_os:
#         :param bool validate_module_id_by_port_name:
#         :return: AutoLoadDetails object
#         """
#         self.entity_table_service.validate_module_id_by_port_name = (
#             validate_module_id_by_port_name
#         )
#         if not resource_model:
#             return
#         self._resource_model = resource_model
#         if not self.system_info_service.is_valid_device_os(supported_os):
#             raise GeneralAutoloadError("Unsupported device OS")
#
#         self.logger.info("*" * 70)
#         self.logger.info("Start SNMP discovery process .....")
#         self.system_info_service.fill_attributes(resource_model)
#
#         entity_chassis_tree_dict = self.entity_table_service.chassis_structure_dict
#
#         if entity_chassis_tree_dict:
#             self._build_structure(entity_chassis_tree_dict.values(), resource_model)
#             self._get_port_channels(resource_model)
#
#         if not self._if_ports_in_entity:
#             self._add_ports_from_iftable()
#
#         autoload_details = resource_model.build(
#             filter_empty_modules=True, use_new_unique_id=True
#         )
#
#         log_autoload_details(self.logger, autoload_details)
#         return autoload_details
#
#     def _build_structure(self, child_list, parent):
#         for element in child_list:
#             if isinstance(element.entity, SnmpEntityTable.ENTITY_CHASSIS):
#                 chassis = self._get_chassis_attributes(element, parent)
#                 self._chassis.update({str(element.entity.index): chassis})
#                 self._build_structure(element.child_list, chassis)
#
#             elif isinstance(element.entity, SnmpEntityTable.ENTITY_MODULE):
#                 module = self._get_module_attributes(element, parent)
#                 if module:
#                     self._build_structure(element.child_list, module)
#
#             elif isinstance(element.entity, SnmpEntityTable.ENTITY_POWER_PORT):
#                 self._get_power_ports(element, parent)
#
#             elif isinstance(element.entity, SnmpEntityTable.ENTITY_PORT):
#                 self._if_ports_in_entity = self._if_ports_in_entity or True
#                 self._get_ports_attributes(element, parent)
#
#     def _add_ports_from_iftable(self):
#         """Get ports data.
#
#         Get resource details and attributes for every port
#         base on data from IF-MIB Table.
#         """
#         self.logger.info("Loading Ports ...")
#
#         for if_index, interface in self.if_table_service.if_ports.items():
#             if self.if_table_service.PORT_VALID_TYPE.search(interface.if_type):
#                 self.logger.debug("Trying to load port {}:".format(interface.port_name))
#                 match = re.search(
#                     r"ethernet(?P<ch_index>\d+)/(?P<if_index>\d+)",
#                     interface.if_descr_name,
#                     re.IGNORECASE,
#                 )
#                 if match:
#                     parent_element = self._chassis.get(
#                         match.groupdict().get("ch_index")
#                     )
#                     if parent_element:
#                         port_object = self._resource_model.entities.Port(
#                             index=if_index, name=interface.port_name.replace("/", "-")
#                         )
#
#                         port_object.mac_address = interface.if_mac
#                         port_object.l2_protocol_type = interface.if_type
#                         port_object.port_description = interface.if_port_description
#                         port_object.bandwidth = interface.if_speed
#                         port_object.mtu = interface.if_mtu
#                         port_object.duplex = interface.duplex
#                         port_object.adjacent = interface.adjacent
#                         port_object.auto_negotiation = interface.auto_negotiation
#                         port_object.ipv4_address = interface.ipv4_address
#                         port_object.ipv6_address = interface.ipv6_address
#
#                         parent_element.connect_port(port_object)
#                         self.logger.info("Added {0} Port".format(interface.port_name))
#                     else:
#                         self.logger.warning(
#                             "Can't find parent element for interface {0}".format(
#                                 interface.port_name
#                             )
#                         )
#
#         self.logger.info("Building Ports completed")
#
#
