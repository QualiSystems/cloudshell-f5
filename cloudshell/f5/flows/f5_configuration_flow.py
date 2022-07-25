from __future__ import annotations

import time
import warnings

from cloudshell.cli.session.session_exceptions import CommandExecutionException
from cloudshell.shell.flows.configuration.basic_flow import (
    AbstractConfigurationFlow,
    ConfigurationType,
    RestoreMethod,
)
from cloudshell.shell.flows.utils.url import RemoteURL

from cloudshell.f5.command_actions.sys_config_actions import (
    F5SysActions,
    F5SysConfigActions,
)


class F5ConfigurationFlow(AbstractConfigurationFlow):
    _local_storage = "/var/local/ucs"

    SUPPORTED_CONFIGURATION_TYPES: set[ConfigurationType] = {
        ConfigurationType.RUNNING,
    }
    SUPPORTED_RESTORE_METHODS: set[RestoreMethod] = {
        RestoreMethod.OVERRIDE,
    }

    def __init__(self, resource_config, logger, cli_handler):
        super(F5ConfigurationFlow, self).__init__(logger, resource_config)
        self._cli_handler = cli_handler

    @property
    def file_system(self):
        return self._local_storage

    def _save_flow(
        self, remote_url: RemoteURL, configuration_type, vrf_management_name
    ):
        save_fail_retries = 10
        save_fail_wait = 3

        filename = f"{remote_url.filename}.ucs"
        local_path = "/".join((self._local_storage, filename))

        with self._cli_handler.get_cli_service(
            self._cli_handler.enable_mode
        ) as session:
            with session.enter_mode(self._cli_handler.config_mode) as config_session:
                sys_config_actions = F5SysConfigActions(
                    config_session, logger=self._logger
                )
                for retry in range(save_fail_retries):
                    output = sys_config_actions.save_config(local_path)
                    if "connection to mcpd has been lost" in output:
                        self._logger.warning(
                            f"save failed becasue mcpd appears "
                            f"to be down (retry {retry}/{save_fail_retries})"
                        )
                        time.sleep(save_fail_wait)
                    else:
                        self._logger.debug("mcpd is up - save success")
                        break
            sys_actions = F5SysActions(session, logger=self._logger)
            sys_actions.upload_config(local_path, remote_url)

    def _restore_flow(
        self, path: RemoteURL, configuration_type, restore_method, vrf_management_name
    ):
        download_file_retries = 10
        download_file_wait = 3

        restart_timeout = 120

        filename = path.filename
        local_path = "{}/{}.ucs".format(self._local_storage, filename)

        with self._cli_handler.get_cli_service(
            self._cli_handler.enable_mode
        ) as session:
            sys_actions = F5SysActions(session, logger=self._logger)

            for retry in range(download_file_retries):
                try:
                    sys_actions.download_config(local_path, path)
                    self._logger.info("Config download success")
                    break
                except CommandExecutionException as e:
                    self._logger.warning(f"Caught exception {e} during config download")
                    self._logger.warning(
                        "retrying... after short delay"
                    )  # todo retries needed?
                    time.sleep(download_file_wait)
                    continue

            with session.enter_mode(self._cli_handler.config_mode) as config_session:
                sys_config_actions = F5SysConfigActions(
                    config_session, logger=self._logger
                )
                sys_config_actions.load_config(local_path)
            sys_actions.reload_device(restart_timeout)

    def orchestration_restore(self, saved_artifact_info, custom_params=None):
        warnings.warn(
            "orchestration_restore is deprecated. Use 'restore' instead",
            DeprecationWarning,
        )
