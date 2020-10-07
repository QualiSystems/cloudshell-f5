from cloudshell.devices.flows.cli_action_flows import DisableSnmpFlow
from cloudshell.snmp.snmp_parameters import SNMPV3Parameters

from cloudshell.f5.command_actions.enable_disable_snmp_actions import (
    SnmpV2Actions,
    SnmpV3Actions,
)


class F5DisableSnmpFlow(DisableSnmpFlow):
    def __init__(self, cli_handler, logger, remove_group=True):
        """Init command.

        :param cli_handler:
        :type cli_handler: JuniperCliHandler
        :param logger:
        :return:
        """
        super(F5DisableSnmpFlow, self).__init__(cli_handler, logger)
        self._cli_handler = cli_handler
        self._remove_group = remove_group

    def execute_flow(self, snmp_parameters):
        """Execute Disable SNMP flow.

        :param cloudshell.snmp.snmp_parameters.SNMPParameters snmp_parameters:
        :return: commands output
        """
        with self._cli_handler.get_cli_service(
            self._cli_handler.config_mode
        ) as cli_service:
            if isinstance(snmp_parameters, SNMPV3Parameters):
                disable_snmp = self._disable_snmp_v3
            else:
                disable_snmp = self._disable_snmp_v2

            disable_snmp(cli_service=cli_service, snmp_parameters=snmp_parameters)

    def _disable_snmp_access(self, snmp_actions):
        """Disable SNMP access.

        :param snmp_actions:
        :return:
        """
        current_snmp_access = snmp_actions.get_current_snmp_access_list()

        if "0.0.0.0/0" in current_snmp_access:
            result = snmp_actions.disable_snmp_access()

            if "0.0.0.0/0" in snmp_actions.get_current_snmp_access_list():
                self._logger.error(
                    "Failed to remove snmp access list: {}".format(result)
                )
                raise Exception(
                    "Failed to remove snmp parameters. Please see logs for details"
                )

    def _disable_snmp_v2(self, cli_service, snmp_parameters):
        """Disable SNMP v2.

        :param cloudshell.cli.cli_service_impl.CliServiceImpl cli_service:
        :param cloudshell.snmp.snmp_parameters.SNMPParameters snmp_parameters:
        :return: commands output
        """
        snmp_community = snmp_parameters.snmp_community

        if not snmp_community:
            raise Exception("SNMP community can not be empty")

        snmp_actions = SnmpV2Actions(cli_service=cli_service, logger=self._logger)
        current_snmp_community_list = snmp_actions.get_current_snmp_communities()

        if snmp_parameters.snmp_community in current_snmp_community_list:
            result = snmp_actions.disable_snmp(
                snmp_community=snmp_parameters.snmp_community
            )

            if (
                snmp_parameters.snmp_community
                in snmp_actions.get_current_snmp_communities()
            ):
                self._logger.error(
                    "Failed to configure snmp community: {}".format(result)
                )
                raise Exception(
                    "Failed to configure snmp parameters. Please see logs for details"
                )

        self._disable_snmp_access(snmp_actions=snmp_actions)

    def _disable_snmp_v3(self, cli_service, snmp_parameters):
        """Disable SNMP v3.

        :param cloudshell.cli.cli_service_impl.CliServiceImpl cli_service:
        :param cloudshell.snmp.snmp_parameters.SNMPParameters snmp_parameters:
        :return: commands output
        """
        snmp_actions = SnmpV3Actions(cli_service=cli_service, logger=self._logger)

        snmp_actions.delete_snmp_user(user=snmp_parameters.snmp_user)
        self._disable_snmp_access(snmp_actions=snmp_actions)
