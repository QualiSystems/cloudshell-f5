from __future__ import annotations

import time
from typing import TYPE_CHECKING, Union

from cloudshell.cli.session.session_exceptions import ExpectedSessionException
from cloudshell.shell.flows.firmware.basic_flow import AbstractFirmwareFlow

from ..command_actions.sys_config_actions import F5SysActions, F5SysConfigActions

if TYPE_CHECKING:
    from logging import Logger

    from cloudshell.shell.flows.utils.url import BasicLocalUrl, RemoteURL
    from cloudshell.shell.standards.firewall.resource_config import (
        FirewallResourceConfig,
    )

    from ..cli.f5_cli_configurator import F5CliConfigurator

    Url = Union[RemoteURL, BasicLocalUrl]


class F5FirmwareFlow(AbstractFirmwareFlow):

    RELOAD_TIMEOUT = 500
    INSTALL_CMD_TIMEOUT = 60
    INSTALL_TIMEOUT = 120
    BOOT_TIMEOUT = 60

    _local_storage = "/shared/images/"

    def __init__(
        self,
        resource_config: FirewallResourceConfig,
        logger: Logger,
        cli_configurator: F5CliConfigurator,
    ):
        super(F5FirmwareFlow, self).__init__(logger, resource_config)
        self._cli_configurator = cli_configurator

    def _load_firmware_flow(
        self, path: Url, vrf_management_name: str | None, timeout: int
    ) -> None:
        filename = path.filename
        local_path = f"{self._local_storage}/{filename}"

        with self._cli_configurator.enable_mode_service() as session:
            sys_actions = F5SysActions(session, logger=self._logger)
            sys_actions.download_config(local_path, path)
            time.sleep(10)
        with self._cli_configurator.config_mode_service() as config_session:
            sys_config_actions = F5SysConfigActions(config_session, logger=self._logger)
            current_volumes_dict = sys_config_actions.show_version_per_volume()
            volume_ids = current_volumes_dict.keys()
            volume_ids = sorted(volume_ids)
            boot_volume = round(volume_ids[-1] + 0.1, 1)
            sys_config_actions.install_firmware(
                filename, boot_volume=f"HD{boot_volume}"
            )
            time.sleep(self.INSTALL_CMD_TIMEOUT)

            max_retries = 20
            retry = 0
            volume_dict = sys_config_actions.show_version_per_volume().get(
                boot_volume, {}
            )
            if volume_dict is None or volume_dict.get("status") is None:
                raise Exception("Failed to load firmware, see logs for details.")

            while (
                "installing" in volume_dict.get("status")
                or "testing" in volume_dict.get("status")
            ) and retry != max_retries:
                time.sleep(self.INSTALL_TIMEOUT)
                try:
                    volume_dict = sys_config_actions.show_version_per_volume().get(
                        boot_volume
                    )
                    if volume_dict is None or volume_dict.get("status") is None:
                        raise Exception(
                            "Failed to load firmware, see logs for details."
                        )
                except ExpectedSessionException:
                    pass
                retry += 1

            if "complete" not in volume_dict.get("status"):
                self._logger.error(f"Failed to load {filename} firmware")
                raise Exception(
                    f"Failed to load {filename} firmware, Please check logs "
                    f"for details."
                )

            sys_config_actions.reload_device_to_certain_volume(
                self.RELOAD_TIMEOUT, f"HD{boot_volume}"
            )
        with self._cli_configurator.config_mode_service() as config_session:
            sys_config_actions = F5SysConfigActions(config_session, logger=self._logger)

            updated_volumes_dict = sys_config_actions.show_version_per_volume()

            if (
                updated_volumes_dict.get(boot_volume, {}).get("is_running", "no")
                == "no"
            ):
                self._logger.error(
                    f"Failed to load {filename} firmware, "
                    f"available boot volumes: {updated_volumes_dict}"
                )
                raise Exception("Failed to update firmware version")
