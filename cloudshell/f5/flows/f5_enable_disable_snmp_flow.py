from cloudshell.snmp.snmp_configurator import EnableDisableSnmpFlowInterface
from cloudshell.snmp.snmp_parameters import (  # todo write ok? used to be v2write
    SNMPWriteParameters,
)

from cloudshell.f5.command_actions.enable_disable_snmp_actions import (
    SnmpV2Actions,
    SnmpV3Actions,
)


class F5EnableDisableSnmpFlow(EnableDisableSnmpFlowInterface):
    def __init__(self, cli_configurator, logger, create_group=True):
        """
        Enable Disable snmp flow.

        :param cloudshell.networking.juniper.cli.juniper_cli_configurator.JuniperCliConfigurator cli_configurator:  # noqa
        :param logging.Logger logger:
        :return:
        """
        self._cli_configurator = cli_configurator
        self._logger = logger
        self._create_group = create_group

    def enable_snmp(self, snmp_parameters):
        with self._cli_configurator.config_mode_service() as cli_service:
            if snmp_parameters.version == snmp_parameters.SnmpVersion.V3:
                self._enable_snmp_v3(cli_service, snmp_parameters)
            else:
                self._enable_snmp(cli_service, snmp_parameters)

    def _enable_snmp(self, cli_service, snmp_parameters):
        """Enable SNMP v2.

        :param cloudshell.cli.cli_service_impl.CliServiceImpl cli_service:
        :param cloudshell.snmp.snmp_parameters.SNMPParameters snmp_parameters:
        :return: commands output
        """
        snmp_community = snmp_parameters.snmp_community

        if not snmp_community:
            raise Exception("SNMP community can not be empty")

        snmp_actions = SnmpV2Actions(cli_service=cli_service, logger=self._logger)

        is_read_only_community = not isinstance(snmp_parameters, SNMPWriteParameters)
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

    def disable_snmp(self, snmp_parameters):
        with self._cli_configurator.config_mode_service() as cli_service:
            if snmp_parameters.version == snmp_parameters.SnmpVersion.V3:
                self._disable_snmp_v3(cli_service, snmp_parameters)
            else:
                self._disable_snmp(cli_service, snmp_parameters)

    def _disable_snmp(self, cli_service, snmp_parameters):
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
