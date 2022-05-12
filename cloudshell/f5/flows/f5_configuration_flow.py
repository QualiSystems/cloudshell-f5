from cloudshell.f5.command_actions.sys_config_actions import (
    F5SysActions,
    F5SysConfigActions,
)
from cloudshell.shell.flows.configuration.basic_flow import AbstractConfigurationFlow
import jsonpickle
import warnings

from cloudshell.logging.utils.decorators import command_logging

### old imports
# from cloudshell.devices.json_request_helper import JsonRequestDeserializer
# from cloudshell.devices.networking_utils import UrlParser, serialize_to_json, command_logging
# from cloudshell.devices.runners.interfaces.configuration_runner_interface import ConfigurationOperationsInterface
from cloudshell.shell.core.interfaces.save_restore import OrchestrationSaveResult, OrchestrationSavedArtifactInfo, \
    OrchestrationSavedArtifact, OrchestrationRestoreRules
###

# todo i may have copypasted all these from the wrong place

class F5ConfigurationFlow(AbstractConfigurationFlow):
    _local_storage = "/var/local/ucs"

    def __init__(self, resource_config, logger, cli_handler):
        super(F5ConfigurationFlow, self).__init__(logger, resource_config)
        # self.cli_configurator = cli_handler
        self._cli_handler = cli_handler

    @property
    def _file_system(self):
        # return "/var/local/ucs"
        return self._local_storage  # todo idk if it's ok implementation but values seem to be the same

    def _save_flow(self, folder_path, configuration_type, vrf_management_name):
        filename = "{}.ucs".format(folder_path.split("/")[-1])
        local_path = "/".join((self._local_storage, filename))
        with self._cli_handler.get_cli_service(
            self._cli_handler.enable_mode
        ) as session:
            with session.enter_mode(self._cli_handler.config_mode) as config_session:
                sys_config_actions = F5SysConfigActions(
                    config_session, logger=self._logger
                )
                sys_config_actions.save_config(local_path)
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

    # todo test
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

        # old code
        # # manipulate params
        # params = dict()
        # if custom_params:
        #     params = jsonpickle.decode(custom_params)
        # save_params = {'folder_path': '', 'configuration_type': 'running', 'return_artifact': True}
        # save_params.update(params.get('custom_params', {}))
        # save_params['folder_path'] = self.get_path(save_params['folder_path'])
        #
        # # invoke regular save
        # saved_artifact = self.save(**save_params)
        #
        # # some artifact hassle
        # import datetime  # kostyl'
        # saved_artifact_info = OrchestrationSavedArtifactInfo(resource_name=self.resource_config.name,
        #                                                      created_date=datetime.datetime.now(),
        #                                                      restore_rules=self.get_restore_rules(),
        #                                                      saved_artifact=saved_artifact)
        # save_response = OrchestrationSaveResult(saved_artifacts_info=saved_artifact_info)
        # self._validate_artifact_info(saved_artifact_info)
        #
        # # return json of response
        # return serialize_to_json(save_response)

    # todo test
    def orchestration_restore(self, saved_artifact_info, custom_params=None):
        warnings.warn(
            "orchestration_restore is deprecated. Use 'restore' instead",
            DeprecationWarning,
        )
