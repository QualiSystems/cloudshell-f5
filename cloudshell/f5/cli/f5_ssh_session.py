import time
from collections import OrderedDict

from cloudshell.cli.session.session_exceptions import SessionException
from cloudshell.cli.session.ssh_session import SSHSession


class F5SSHSession(SSHSession):
    def _connect_actions(self, prompt, logger):
        action_map = OrderedDict()
        cli_action_key = r"INOPERATIVE|[Ii]noperative"

        def action(session, sess_logger):
            time.sleep(15)
            raise SessionException("System inoperative")

        action_map[cli_action_key] = action
        self.hardware_expect(
            None,
            expected_string=prompt,
            action_map=action_map,
            timeout=self._timeout,
            logger=logger,
        )
        self._on_session_start(logger)
