from __future__ import annotations

import re
import time
from collections import OrderedDict
from typing import TYPE_CHECKING, Callable, Dict

from cloudshell.cli.command_template.command_template_executor import (
    CommandTemplateExecutor,
)
from cloudshell.cli.session.session_exceptions import SessionException
from cloudshell.shell.flows.utils.url import RemoteURL

from cloudshell.f5.command_templates import f5_config_templates

if TYPE_CHECKING:
    from logging import Logger

    from cloudshell.cli.service.cli_service import CliService


class F5SysConfigActions(object):
    def __init__(self, cli_service: CliService, logger: Logger):
        self._cli_service = cli_service
        self._logger = logger

    def save_config(self, file_path, retries=5, timeout=10):
        tally = 0
        while tally < retries:
            output = CommandTemplateExecutor(
                self._cli_service,
                f5_config_templates.MCPD_STATE,
                timeout=180,
            ).execute_command()

            if re.search(r"[Rr]unning\s+[Pp]hase\s+running", output) is not None:
                break
            else:
                time.sleep(timeout)
                tally += 1
                self._logger.warning(
                    f"MCPD service is not in the state running, waiting {timeout} sec."
                )
        else:
            raise Exception(
                "MCPD service is not running, cannot proceed with save configuration."
            )

        output = CommandTemplateExecutor(
            self._cli_service,
            f5_config_templates.SAVE_CONFIG_LOCALLY,
            timeout=180,
        ).execute_command(file_path=file_path)
        return output

    def load_config(self, file_path):
        output = CommandTemplateExecutor(
            self._cli_service, f5_config_templates.LOAD_CONFIG_LOCALLY, timeout=180
        ).execute_command(file_path=file_path)
        return output

    def install_firmware(self, file_path, boot_volume):
        # todo not in standard?
        output = CommandTemplateExecutor(
            self._cli_service, f5_config_templates.INSTALL_FIRMWARE, timeout=180
        ).execute_command(file_path=file_path, boot_volume=boot_volume)
        return output

    def show_version_per_volume(self):
        result = CommandTemplateExecutor(
            self._cli_service, f5_config_templates.SHOW_VERSION_PER_VOLUME, timeout=180
        ).execute_command()
        result_iter = re.finditer(
            r"HD(?P<volume>\S+)\s+(big[- ]ip|none)\s+"
            r"(?P<version>\d+(.\d+)+|none)\s+\S*\s*"
            r"(?P<is_running>yes|no)\s+"
            r"(?P<status>complete|installing\s*\d+.\d+|testing\s*archive:\s*\S+)?",
            result,
            re.IGNORECASE,
        )

        return {float(x.groupdict().get("volume")): x.groupdict() for x in result_iter}

    def reload_device_to_certain_volume(
        self,
        timeout: int,
        volume: str,
        action_map: Dict[str, Callable] = None,
        error_map: Dict[str, str] = None,
    ):
        """Reload device.

        :param timeout: session reconnect timeout
        :param action_map: actions will be taken during executing commands
        :param error_map: errors will be raised during executing commands
        """
        try:
            CommandTemplateExecutor(
                self._cli_service,
                f5_config_templates.RELOAD_TO_CERTAIN_VOLUME,
                action_map=action_map,
                error_map=error_map,
            ).execute_command(volume=volume)

        except SessionException:
            pass

        self._logger.info("Device rebooted, starting reconnect")
        time.sleep(300)
        self._cli_service.reconnect(timeout)

    def enable_tftp(self, tftp_server: str) -> str:
        out = self._cli_service.send_command(f5_config_templates.DISABLE_TFTP_COMMAND)
        out += self._cli_service.send_command(
            f5_config_templates.ENABLE_TFTP_COMMAND.replace(
                "__TFTP_SERVER__", tftp_server
            )
        )
        return out

    def disable_tftp(self) -> str:
        out = self._cli_service.send_command(f5_config_templates.DISABLE_TFTP_COMMAND)
        return out


class F5SysActions(object):
    def __init__(self, cli_service: CliService, logger: Logger):
        self._cli_service = cli_service
        self._logger = logger

    def download_config(self, file_path: str, remote_url: RemoteURL):
        """Download file from SCP/FTP/TFTP Server."""
        self._logger.debug(f"Downloading through {remote_url.scheme}")
        if remote_url.scheme == "scp":
            password_prompt_action_map = OrderedDict(
                [
                    (
                        r"[Pp]assword:?",
                        lambda session, logger: session.send_line(
                            remote_url.password, logger
                        ),
                    ),
                    (
                        r"continue\s+connecting\s\(yes\/no\)\?",
                        lambda session, logger: session.send_line("yes", logger),
                    ),
                ]
            )
            output = CommandTemplateExecutor(
                self._cli_service,
                f5_config_templates.DOWNLOAD_FILE_TO_DEVICE_SCP,
                action_map=password_prompt_action_map,
            ).execute_command(remote_url=remote_url, local_path=file_path)
        else:
            output = CommandTemplateExecutor(
                self._cli_service,
                f5_config_templates.DOWNLOAD_FILE_TO_DEVICE,
                timeout=180,
            ).execute_command(file_path=file_path, url=remote_url)
        return output

    def upload_config(self, file_path: str, remote_url: RemoteURL) -> None:
        """Upload file to FTP/TFTP Server."""
        # curl: (55) Network is unreachable
        if remote_url.scheme == "scp":
            password_prompt_action_map = OrderedDict(
                [
                    (
                        r"[Pp]assword:?",
                        lambda session, logger: session.send_line(
                            remote_url.password, logger
                        ),
                    ),
                    (
                        r"continue\s+connecting\s\(yes\/no\)\?",
                        lambda session, logger: session.send_line("yes", logger),
                    ),
                ]
            )
            CommandTemplateExecutor(
                self._cli_service,
                f5_config_templates.UPLOAD_FILE_FROM_DEVICE_SCP,
                action_map=password_prompt_action_map,
            ).execute_command(remote_url=remote_url, local_path=file_path)
        else:
            CommandTemplateExecutor(
                self._cli_service, f5_config_templates.UPLOAD_FILE_FROM_DEVICE
            ).execute_command(file_path=file_path, url=remote_url)
        self._logger.debug("Upload config success")

    def reload_device(self, timeout, action_map=None, error_map=None):
        """Reload device.

        :param timeout: session reconnect timeout
        :param action_map: actions will be taken during executing commands
        :param error_map: errors will be raised during executing commands
        """
        try:
            CommandTemplateExecutor(
                self._cli_service,
                f5_config_templates.RELOAD,
                action_map=action_map,
                error_map=error_map,
            ).execute_command()

        except SessionException:
            pass
        self._logger.info("Device rebooted, starting reconnect")

        self._cli_service.reconnect(timeout)

    def copy_config(self, source_boot_volume, target_boot_volume):
        CommandTemplateExecutor(
            self._cli_service, f5_config_templates.COPY_CONFIG, timeout=180
        ).execute_command(src_config=source_boot_volume, dst_config=target_boot_volume)

    def remove_file(self, file_path):
        output = CommandTemplateExecutor(
            self._cli_service, f5_config_templates.REMOVE_FILE, timeout=180
        ).execute_command(file_path=file_path)
        return output
