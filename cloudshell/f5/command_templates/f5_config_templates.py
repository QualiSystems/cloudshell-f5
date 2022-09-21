from collections import OrderedDict

from cloudshell.cli.command_template.command_template import CommandTemplate

CURL_ERROR_MAP = OrderedDict(
    [
        (r"[Nn]etwork is unreachable", "Curl: network is unreachable"),
        (r"curl:|[Ff]ail|[Ee]rror", "Uploading/downloading file via CURL failed"),
    ]
)
GENERIC_ERROR_MAP = OrderedDict([(r"[Ff]ail|[Ee]rror", "Generic error occurred")])

SCP_ERROR_MAP = OrderedDict(
    [
        (r"[Nn]o\s+such\s+file\s+or\s+directory", "File not found"),
        (r"[Pp]ermission\s+denied", "Permission denied"),
    ]
)

ACTION_MAP = OrderedDict(
    [
        (
            r"\([Yy](es)?/[Nn](o)?\)",
            lambda session, logger: session.send_line("y", logger),
        )
    ]
)

MCPD_ERROR = "The connection to mcpd has been lost"
CONFIG_ERROR_MAP = OrderedDict(
    [(r"connection\s+to\s+mcpd\s+has\s+been\s+lost", MCPD_ERROR)]
)

MCPD_STATE = CommandTemplate("show sys mcp-state")

SAVE_CONFIG_LOCALLY = CommandTemplate(
    "save sys ucs {file_path} no-private-key", error_map=CONFIG_ERROR_MAP
)
LOAD_CONFIG_LOCALLY = CommandTemplate(
    "load sys ucs {file_path} no-license", action_map=ACTION_MAP
)
LOAD_CLUSTER_CONFIG_LOCALLY = CommandTemplate(
    "load sys ucs {file_path} no-license include-chassis-level-config"
)

UPLOAD_FILE_FROM_DEVICE = CommandTemplate(
    "curl --insecure --upload-file {file_path} {url}", error_map=CURL_ERROR_MAP
)
UPLOAD_FILE_FROM_DEVICE_SCP = CommandTemplate(
    "scp {local_path} {remote_url.username}@{remote_url.host}:{remote_url.path}",
    error_map=OrderedDict(**GENERIC_ERROR_MAP, **SCP_ERROR_MAP),
)

DOWNLOAD_FILE_TO_DEVICE = CommandTemplate(
    "curl --insecure {url} -o {file_path} ", error_map=CURL_ERROR_MAP
)
DOWNLOAD_FILE_TO_DEVICE_SCP = CommandTemplate(
    "scp {remote_url.username}@{remote_url.host}:{remote_url.path} {local_path}",
    error_map=OrderedDict(**GENERIC_ERROR_MAP, **SCP_ERROR_MAP),
)

INSTALL_FIRMWARE = CommandTemplate(
    "install sys software image {file_path} volume {boot_volume} create-volume",
    error_map=OrderedDict(
        [
            (
                r"[Ss]yntax\s+[Ee]rror",
                "Failed to install firmware, Please check logs for details",
            ),
            (
                r"[Dd]ata\s+[Ii]nput\s+[Ee]rror:",
                "Failed to install firmware, see logs for more details.",
            ),
        ]
    ),
)

RELOAD = CommandTemplate("reboot")
RELOAD_TO_CERTAIN_VOLUME = CommandTemplate("reboot volume {volume}")

COPY_CONFIG = CommandTemplate("cpcfg --source={src_config} {dst_config}")
# cpcfg --source=HD1.2 HD1.3

SHOW_VERSION_PER_VOLUME = CommandTemplate("show sys software | grep HD")
REMOVE_FILE = CommandTemplate("rm -rf {file_path}")

ENABLE_TFTP_COMMAND = (
    "modify security firewall management-ip-rules rules "
    "add { QUALI_SHELL_TFTP { place-before first action "
    "accept ip-protocol any source { addresses add { __TFTP_SERVER__ { } } } } }"
)
DISABLE_TFTP_COMMAND = (
    "modify security firewall management-ip-rules rules delete { QUALI_SHELL_TFTP }"
)
