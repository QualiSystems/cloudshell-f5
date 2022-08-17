import re
import time
from collections import OrderedDict

from cloudshell.cli.command_template.command_template_executor import (
    CommandTemplateExecutor,
)
from cloudshell.cli.session.session_exceptions import (
    CommandExecutionException,
    SessionException,
)
from cloudshell.shell.flows.utils.url import RemoteURL

from cloudshell.f5.command_templates import f5_config_templates
from cloudshell.f5.command_templates.f5_config_templates import MCPD_ERROR


class F5SysConfigActions(object):
    def __init__(self, cli_service, logger):
        self._cli_service = cli_service
        self._logger = logger

    def save_config(self, file_path, retries=5):
        tally = 0
        while tally < retries:
            try:
                output = CommandTemplateExecutor(
                    self._cli_service,
                    f5_config_templates.SAVE_CONFIG_LOCALLY,
                    timeout=180,
                ).execute_command(file_path=file_path)
                return output
            except CommandExecutionException as e:
                tally += 1
                if MCPD_ERROR not in str(e):
                    raise e
        raise Exception(f"Retries for '{MCPD_ERROR}' exceeded {retries}")

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
        self, timeout, volume, action_map=None, error_map=None
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


class F5SysActions(object):
    def __init__(self, cli_service, logger):
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
            self._logger.info("Device rebooted, starting reconnect")

        # todo AttributeError: 'NoneType' object has no attribute 'enter_actions'
        try:
            self._cli_service.reconnect(timeout)
        except AttributeError as e:
            self._logger.debug(f"Exception {e} while reconnecting, retrying")
            time.sleep(5)
            self._cli_service.reconnect(30)

    def copy_config(self, source_boot_volume, target_boot_volume):
        CommandTemplateExecutor(
            self._cli_service, f5_config_templates.COPY_CONFIG, timeout=180
        ).execute_command(src_config=source_boot_volume, dst_config=target_boot_volume)

    def remove_file(self, file_path):
        output = CommandTemplateExecutor(
            self._cli_service, f5_config_templates.REMOVE_FILE, timeout=180
        ).execute_command(file_path=file_path)
        return output
