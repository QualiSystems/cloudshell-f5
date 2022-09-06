import time
from collections import OrderedDict

from cloudshell.cli.session.session_exceptions import SessionException
from cloudshell.cli.session.telnet_session import TelnetSession


class F5TelnetSession(TelnetSession):
    def _connect_actions(self, prompt, logger):
        action_map = OrderedDict()
        action_map[
            "[Ll]ogin:|[Uu]ser:|[Uu]sername:"
        ] = lambda session, logger: session.send_line(session.username, logger)
        action_map["[Pp]assword:"] = lambda session, logger: session.send_line(
            session.password, logger
        )

        cli_action_key = r"INOPERATIVE|[Ii]noperative"

        def action(session, sess_logger):
            time.sleep(15)
            raise SessionException("System inoperative")

        action_map[cli_action_key] = action
        self.hardware_expect(
            None,
            expected_string=prompt,
            timeout=self._timeout,
            logger=logger,
            action_map=action_map,
        )
        self._on_session_start(logger)
