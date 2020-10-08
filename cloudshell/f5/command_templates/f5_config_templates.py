from collections import OrderedDict

from cloudshell.cli.command_template.command_template import CommandTemplate

CURL_ERROR_MAP = OrderedDict(
    [(r"curl:|[Ff]ail|[Ee]rror", "Uploading/downloading file via CURL failed")]
)
ACTION_MAP = OrderedDict(
    [
        (
            r"\([Yy](es)?/[Nn](o)?\)",
            lambda session, logger: session.send_line("y", logger),
        )
    ]
)


SAVE_CONFIG_LOCALLY = CommandTemplate("save /sys ucs {file_path} no-private-key")
LOAD_CONFIG_LOCALLY = CommandTemplate(
    "load /sys ucs {file_path} no-license", action_map=ACTION_MAP
)
LOAD_CLUSTER_CONFIG_LOCALLY = CommandTemplate(
    "load /sys ucs {file_path} no-license include-chassis-level-config"
)

UPLOAD_FILE_FROM_DEVICE = CommandTemplate(
    "curl --insecure --upload-file {file_path} {url}", error_map=CURL_ERROR_MAP
)
DOWNLOAD_FILE_TO_DEVICE = CommandTemplate(
    "curl --insecure {url} -o {file_path} ", error_map=CURL_ERROR_MAP
)
INSTALL_FIRMWARE = CommandTemplate(
    "install sys software image {file_path} volume {boot_volume} create-volume",
    error_map=OrderedDict(
        [
            (
                r"[Ss]yntax\s+[Ee]rror",
                "Failed to install firmware, Please check logs for details",
            )
        ]
    ),
)

RELOAD = CommandTemplate("reboot")
RELOAD_TO_CERTAIN_VOLUME = CommandTemplate("reboot volume {volume}")

COPY_CONFIG = CommandTemplate("cpcfg --source={src_config} {dst_config}")
# cpcfg --source=HD1.2 HD1.3

SHOW_VERSION_PER_VOLUME = CommandTemplate("show sys software | grep HD")
