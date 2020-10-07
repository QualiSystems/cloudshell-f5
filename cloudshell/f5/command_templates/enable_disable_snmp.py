from collections import OrderedDict

from cloudshell.cli.command_template.command_template import CommandTemplate

ERROR_MAP = OrderedDict(
    {
        r"[Ss]yntax\s*[Ee]rror": "Failed to initialize snmp. "
        "Please check Logs for details."
    }
)

ENABLE_SNMP_ACCESS = CommandTemplate(
    "modify sys snmp allowed-addresses add {{ 0.0.0.0/0 }}", error_map=ERROR_MAP
)
DISABLE_SNMP_ACCESS = CommandTemplate(
    "modify sys snmp allowed-addresses delete {{ 0.0.0.0/0 }}", error_map=ERROR_MAP
)
SHOW_SNMP_ACCESS = CommandTemplate(
    "list sys snmp allowed-addresses", error_map=ERROR_MAP
)

CREATE_SNMP_COMMUNITY = CommandTemplate(
    "modify /sys snmp communities add {{ {snmp_community} {{ access {read_access} "
    "community-name {snmp_community}}} }}",
    error_map=ERROR_MAP,
)
REMOVE_SNMP_COMMUNITY = CommandTemplate(
    "modify /sys snmp communities delete {{ {snmp_community} }}", error_map=ERROR_MAP
)
SHOW_SNMP_COMMUNITY = CommandTemplate(
    "list /sys snmp communities | grep  community-name", error_map=ERROR_MAP
)

ADD_SNMP_USER = CommandTemplate(
    "modify sys snmp users add {{ {user} {{ username {user} auth-protocol "
    "{auth_protocol} privacy-protocol {priv_protocol} security-level {security_level} "
    "oid-subset .1 auth-password '{password}' privacy-password '{priv_password}' }} }}",
    error_map=ERROR_MAP,
)

DELETE_SNMP_USER = CommandTemplate(
    "modify sys snmp users delete {{ {user} }}", error_map=ERROR_MAP
)
