from __future__ import annotations

from logging import Logger
from typing import TYPE_CHECKING

from cloudshell.shell.flows.configuration.basic_flow import (
    AbstractConfigurationFlow,
    ConfigurationType,
    RestoreMethod,
)
from cloudshell.shell.flows.utils.url import BasicLocalUrl

from ..command_actions.sys_config_actions import F5SysActions, F5SysConfigActions

if TYPE_CHECKING:
    from typing import Union

    from cloudshell.shell.flows.utils.url import RemoteURL
    from cloudshell.shell.standards.resource_config_generic_models import (
        GenericBackupConfig,
    )

    from ..cli.f5_cli_configurator import F5CliConfigurator

    Url = Union[RemoteURL, BasicLocalUrl]


class F5ConfigurationFlow(AbstractConfigurationFlow):
    _local_storage = "/var/local/ucs"

    SUPPORTED_CONFIGURATION_TYPES: set[ConfigurationType] = {
        ConfigurationType.RUNNING,
    }
    SUPPORTED_RESTORE_METHODS: set[RestoreMethod] = {
        RestoreMethod.OVERRIDE,
    }
    LOCAL_FILE_EXT = ".ucs"

    def __init__(
        self,
        resource_config: GenericBackupConfig,
        logger: Logger,
        cli_configurator: F5CliConfigurator,
    ):
        super(F5ConfigurationFlow, self).__init__(logger, resource_config)
        self._cli_configurator = cli_configurator

    @property
    def file_system(self) -> str:
        return self._local_storage

    def _save_flow(
        self,
        file_dst_url: Url,
        configuration_type: ConfigurationType,
        vrf_management_name: str | None,
    ) -> str:
        if isinstance(file_dst_url, BasicLocalUrl):
            local_path = file_dst_url.safe_url
            remote = False
        else:
            filename = file_dst_url.filename + self.LOCAL_FILE_EXT
            local_path = "/".join((self._local_storage, filename))
            remote = True

        with self._cli_configurator.get_cli_service(
            self._cli_configurator.enable_mode
        ) as session:
            with session.enter_mode(
                self._cli_configurator.config_mode
            ) as config_session:
                sys_config_actions = F5SysConfigActions(
                    config_session, logger=self._logger
                )
                sys_config_actions.save_config(local_path)
            if remote:
                sys_actions = F5SysActions(session, logger=self._logger)
                if file_dst_url.scheme.lower() == "tftp":
                    with session.enter_mode(self._cli_configurator.config_mode):
                        sys_config_actions.enable_tftp(file_dst_url.host)
                try:
                    sys_actions.upload_config(local_path, file_dst_url)
                finally:
                    if file_dst_url.scheme.lower() == "tftp":
                        with session.enter_mode(self._cli_configurator.config_mode):
                            sys_config_actions.disable_tftp()

                sys_actions.remove_file(local_path)
            return file_dst_url.filename

    def _restore_flow(
        self, path: Url, configuration_type, restore_method, vrf_management_name
    ) -> None:
        restart_timeout = 240

        if isinstance(path, BasicLocalUrl):
            remote = False
            local_path = path.url
        else:
            remote = True
            filename = path.filename
            local_path = (
                "{}/{}".format(self._local_storage, filename) + self.LOCAL_FILE_EXT
            )

        with self._cli_configurator.get_cli_service(
            self._cli_configurator.enable_mode
        ) as session:
            sys_actions = F5SysActions(session, logger=self._logger)
            sys_config_actions = F5SysConfigActions(session, logger=self._logger)
            if remote:
                if path.scheme.lower() == "tftp":
                    with session.enter_mode(self._cli_configurator.config_mode):
                        sys_config_actions.enable_tftp(path.host)
                try:
                    sys_actions.download_config(local_path, path)
                finally:
                    if path.scheme.lower() == "tftp":
                        with session.enter_mode(self._cli_configurator.config_mode):
                            sys_config_actions.disable_tftp()
            with session.enter_mode(
                self._cli_configurator.config_mode
            ) as config_session:
                sys_config_actions = F5SysConfigActions(
                    config_session, logger=self._logger
                )
                sys_config_actions.load_config(local_path)
            sys_actions.remove_file(local_path)
            sys_actions.reload_device(restart_timeout)
