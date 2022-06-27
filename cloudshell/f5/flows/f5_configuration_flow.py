import time
import warnings

import jsonpickle

from cloudshell.shell.flows.configuration.basic_flow import AbstractConfigurationFlow

from cloudshell.f5.command_actions.sys_config_actions import (
    F5SysActions,
    F5SysConfigActions,
)


class F5ConfigurationFlow(AbstractConfigurationFlow):
    _local_storage = "/var/local/ucs"

    def __init__(self, resource_config, logger, cli_handler):
        super(F5ConfigurationFlow, self).__init__(logger, resource_config)
        self._cli_handler = cli_handler

    @property
    def _file_system(self):
        return self._local_storage

    def _save_flow(self, folder_path, configuration_type, vrf_management_name):
        save_fail_retries = 10
        save_fail_wait = 3

        filename = "{}.ucs".format(folder_path.split("/")[-1])
        local_path = "/".join((self._local_storage, filename))
        with self._cli_handler.get_cli_service(
            self._cli_handler.enable_mode
        ) as session:
            with session.enter_mode(self._cli_handler.config_mode) as config_session:
                sys_config_actions = F5SysConfigActions(
                    config_session, logger=self._logger
                )
                for retry in range(save_fail_retries):
                    # todo cleanup
                    from cloudshell.cli.session.session_exceptions import (
                        CommandExecutionException,
                    )

                    try:
                        output = sys_config_actions.save_config(local_path)
                    except CommandExecutionException as e:
                        self._logger.warning(
                            f"caught exception {e} during save attempt"
                        )
                        self._logger.warning("retrying... after short delay")
                        time.sleep(save_fail_wait)
                        continue

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
            sys_actions.upload_config(local_path, folder_path)

    def _restore_flow(
        self, path, configuration_type, restore_method, vrf_management_name
    ):
        filename = path.split("/")[-1]
        local_path = "{}/{}".format(self._local_storage, filename)

        with self._cli_handler.get_cli_service(
            self._cli_handler.enable_mode
        ) as session:
            sys_actions = F5SysActions(session, logger=self._logger)
            sys_actions.download_config(local_path, path)
            with session.enter_mode(self._cli_handler.config_mode) as config_session:
                sys_config_actions = F5SysConfigActions(
                    config_session, logger=self._logger
                )
                sys_config_actions.load_config(local_path)
            sys_actions.reload_device(120)

    def orchestration_save(self, mode="shallow", custom_params=None):
        save_params = {
            "folder_path": "",
            "configuration_type": "running",
            "return_full_path": True,
        }
        params = {}
        if custom_params:
            params = jsonpickle.decode(custom_params)

        save_params.update(params.get("custom_params", {}))
        save_params["folder_path"] = self._get_path(save_params["folder_path"])

        path = self.save(**save_params)

        return path

    def orchestration_restore(self, saved_artifact_info, custom_params=None):
        warnings.warn(
            "orchestration_restore is deprecated. Use 'restore' instead",
            DeprecationWarning,
        )
