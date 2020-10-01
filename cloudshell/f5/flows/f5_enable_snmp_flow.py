from cloudshell.devices.flows.cli_action_flows import EnableSnmpFlow
from cloudshell.snmp.snmp_parameters import SNMPV2WriteParameters, SNMPV3Parameters

from cloudshell.f5.command_actions.enable_disable_snmp_actions import (
    SnmpV2Actions,
    SnmpV3Actions,
)


class F5EnableSnmpFlow(EnableSnmpFlow):
    def __init__(self, cli_handler, logger, create_group=True):
        """Init command.

        :param cli_handler:
        :param logger:
        :return:
        """
        super(F5EnableSnmpFlow, self).__init__(cli_handler, logger)
        self._cli_handler = cli_handler
        self._create_group = create_group

    def execute_flow(self, snmp_parameters):
        """Execute Enable SNMP flow.

        :param cloudshell.snmp.snmp_parameters.SNMPParameters snmp_parameters:
        :return: commands output
        """
        with self._cli_handler.get_cli_service(
            self._cli_handler.config_mode
        ) as cli_service:
            if isinstance(snmp_parameters, SNMPV3Parameters):
                enable_snmp = self._enable_snmp_v3
            else:
                enable_snmp = self._enable_snmp_v2

            enable_snmp(cli_service=cli_service, snmp_parameters=snmp_parameters)

    def _enable_snmp_access(self, snmp_actions):
        """Enable SNMP access.

        :param snmp_actions:
        :return:
        """
        current_snmp_access = snmp_actions.get_current_snmp_access_list()

        if "0.0.0.0/0" not in current_snmp_access:
            result = snmp_actions.enable_snmp_access()

            if "0.0.0.0/0" not in snmp_actions.get_current_snmp_access_list():
                self._logger.error(
                    "Failed to configure snmp access list: {}".format(result)
                )
                raise Exception(
                    "Failed to configure snmp parameters. Please see logs for details"
                )

    def _enable_snmp_v2(self, cli_service, snmp_parameters):
        """Enable SNMP v2.

        :param cloudshell.cli.cli_service_impl.CliServiceImpl cli_service:
        :param cloudshell.snmp.snmp_parameters.SNMPParameters snmp_parameters:
        :return: commands output
        """
        snmp_community = snmp_parameters.snmp_community

        if not snmp_community:
            raise Exception("SNMP community can not be empty")

        snmp_actions = SnmpV2Actions(cli_service=cli_service, logger=self._logger)

        is_read_only_community = not isinstance(snmp_parameters, SNMPV2WriteParameters)
        current_snmp_community_list = snmp_actions.get_current_snmp_communities()

        if snmp_parameters.snmp_community not in current_snmp_community_list:
            result = snmp_actions.enable_snmp(
                snmp_parameters.snmp_community, is_read_only_community
            )

            if (
                snmp_parameters.snmp_community
                not in snmp_actions.get_current_snmp_communities()
            ):
                self._logger.error(
                    "Failed to configure snmp community: {}".format(result)
                )
                raise Exception(
                    "Failed to configure snmp parameters. Please see logs for details"
                )

        self._enable_snmp_access(snmp_actions=snmp_actions)

    def _enable_snmp_v3(self, cli_service, snmp_parameters):
        """Enable SNMP v3.

        :param cloudshell.cli.cli_service_impl.CliServiceImpl cli_service:
        :param cloudshell.snmp.snmp_parameters.SNMPParameters snmp_parameters:
        :return: commands output
        """
        snmp_actions = SnmpV3Actions(cli_service=cli_service, logger=self._logger)

        snmp_actions.add_snmp_user(
            user=snmp_parameters.snmp_user,
            password=snmp_parameters.snmp_password,
            priv_key=snmp_parameters.snmp_private_key,
            auth_proto=snmp_parameters.auth_protocol,
            priv_proto=snmp_parameters.private_key_protocol,
        )

        self._enable_snmp_access(snmp_actions=snmp_actions)
