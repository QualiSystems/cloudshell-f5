import re

from cloudshell.cli.command_template.command_template_executor import (
    CommandTemplateExecutor,
)
from cloudshell.snmp.snmp_parameters import SNMPV3Parameters

from cloudshell.f5.command_templates import enable_disable_snmp


class BaseSnmpActions(object):
    def __init__(self, cli_service, logger):
        """Init command.

        :param cli_service:
        :param logger:
        """
        self._cli_service = cli_service
        self._logger = logger

    def get_current_snmp_access_list(self, action_map=None, error_map=None):
        """Retrieve current snmp communities.

        :param action_map: actions will be taken during executing commands
        :param error_map: errors will be raised during executing commands
        :return:
        """
        result = CommandTemplateExecutor(
            cli_service=self._cli_service,
            command_template=enable_disable_snmp.SHOW_SNMP_ACCESS,
            action_map=action_map,
            error_map=error_map,
        ).execute_command()

        return re.sub(r"^.*{.*{\s|\s}.*}.*$", "", result, flags=re.DOTALL).split(" ")

    def enable_snmp_access(self, action_map=None, error_map=None):
        """Enable SNMP view on the device.

        :param action_map: actions will be taken during executing commands
        :param error_map: errors will be raised during executing commands
        """
        return CommandTemplateExecutor(
            cli_service=self._cli_service,
            command_template=enable_disable_snmp.ENABLE_SNMP_ACCESS,
            action_map=action_map,
            error_map=error_map,
        ).execute_command()

    def disable_snmp_access(self, action_map=None, error_map=None):
        """Disable SNMP community on the device.

        :param action_map: actions will be taken during executing commands
        :param error_map: errors will be raised during executing commands
        """
        return CommandTemplateExecutor(
            cli_service=self._cli_service,
            command_template=enable_disable_snmp.DISABLE_SNMP_ACCESS,
            action_map=action_map,
            error_map=error_map,
        ).execute_command()


class SnmpV2Actions(BaseSnmpActions):
    READ_ONLY = "ro"
    READ_WRITE = "rw"

    def get_current_snmp_communities(self, action_map=None, error_map=None):
        """Retrieve current snmp communities.

        :param action_map: actions will be taken during executing commands
        :param error_map: errors will be raised during executing commands
        :return:
        """
        result = CommandTemplateExecutor(
            cli_service=self._cli_service,
            command_template=enable_disable_snmp.SHOW_SNMP_COMMUNITY,
            action_map=action_map,
            error_map=error_map,
        ).execute_command()

        return re.findall(r"community-name\s+(\S+)", result)

    def enable_snmp(
        self,
        snmp_community,
        is_read_only_community=True,
        action_map=None,
        error_map=None,
    ):
        """Enable SNMP on the device.

        :param is_read_only_community: indicates if community access should be read only
        :param snmp_community: community name
        :param action_map: actions will be taken during executing commands
        :param error_map: errors will be raised during executing commands
        """
        read_only = self.READ_ONLY if is_read_only_community else self.READ_WRITE

        return CommandTemplateExecutor(
            cli_service=self._cli_service,
            command_template=enable_disable_snmp.CREATE_SNMP_COMMUNITY,
            action_map=action_map,
            error_map=error_map,
        ).execute_command(
            snmp_community=snmp_community,
            read_access=read_only,
        )

    def disable_snmp(self, snmp_community, action_map=None, error_map=None):
        """Disable SNMP community on the device.

        :param snmp_community: community name
        :param action_map: actions will be taken during executing commands
        :param error_map: errors will be raised during executing commands
        """
        return CommandTemplateExecutor(
            cli_service=self._cli_service,
            command_template=enable_disable_snmp.REMOVE_SNMP_COMMUNITY,
            action_map=action_map,
            error_map=error_map,
        ).execute_command(snmp_community=snmp_community)


class SnmpV3Actions(BaseSnmpActions):
    AUTH_COMMAND_MAP = {
        SNMPV3Parameters.AUTH_NO_AUTH: "none",
        SNMPV3Parameters.AUTH_MD5: "md5",
        SNMPV3Parameters.AUTH_SHA: "sha",
    }

    PRIV_COMMAND_MAP = {
        SNMPV3Parameters.PRIV_NO_PRIV: "none",
        SNMPV3Parameters.PRIV_DES: "des",
        SNMPV3Parameters.PRIV_AES128: "aes",
        # SNMPV3Parameters.PRIV_3DES: "",  # not supported by device  # noqa
        # SNMPV3Parameters.PRIV_AES192: "encrypt-aes",  # not supported by device  # noqa
        # SNMPV3Parameters.PRIV_AES256: "encrypt-aes"   # not supported by device  # noqa
    }

    SECURITY_LEVEL_AUTH_PRIVACY = "auth-privacy"
    SECURITY_LEVEL_AUTH_NO_PRIVACY = "auth-no-privacy"
    SECURITY_LEVEL_NO_AUTH_NO_PRIVACY = "no-auth-no-privacy"

    def _get_security_level(self, auth_proto, priv_proto):
        """Get security level.

        :param auth_proto:
        :param priv_proto:
        :return:
        """
        if all(
            [
                auth_proto == SNMPV3Parameters.AUTH_NO_AUTH,
                priv_proto == SNMPV3Parameters.PRIV_NO_PRIV,
            ]
        ):
            return self.SECURITY_LEVEL_NO_AUTH_NO_PRIVACY
        elif priv_proto == SNMPV3Parameters.PRIV_NO_PRIV:
            return self.SECURITY_LEVEL_AUTH_NO_PRIVACY

        return self.SECURITY_LEVEL_AUTH_PRIVACY

    def add_snmp_user(
        self,
        user,
        password,
        priv_key,
        auth_proto,
        priv_proto,
        action_map=None,
        error_map=None,
    ):
        """Add SNMP v3 user.

        :param user:
        :param password:
        :param priv_key:
        :param auth_proto:
        :param priv_proto:
        :param action_map:
        :param error_map:
        :return:
        """
        try:
            auth_protocol = self.AUTH_COMMAND_MAP[auth_proto]
        except KeyError:
            raise Exception(
                "Authentication protocol {} is not supported".format(auth_proto)
            )

        try:
            priv_protocol = self.PRIV_COMMAND_MAP[priv_proto]
        except KeyError:
            raise Exception("Privacy Protocol {} is not supported".format(priv_proto))

        security_level = self._get_security_level(
            auth_proto=auth_proto, priv_proto=priv_proto
        )

        return CommandTemplateExecutor(
            cli_service=self._cli_service,
            command_template=enable_disable_snmp.ADD_SNMP_USER,
            action_map=action_map,
            error_map=error_map,
        ).execute_command(
            user=user,
            password=password,
            auth_protocol=auth_protocol,
            priv_password=priv_key,
            priv_protocol=priv_protocol,
            security_level=security_level,
        )

    def delete_snmp_user(self, user, action_map=None, error_map=None):
        """Delete SNMP v3 user.

        :param user:
        :param action_map:
        :param error_map:
        :return:
        """
        return CommandTemplateExecutor(
            cli_service=self._cli_service,
            command_template=enable_disable_snmp.DELETE_SNMP_USER,
            action_map=action_map,
            error_map=error_map,
        ).execute_command(user=user)
