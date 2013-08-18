import logging
import subprocess
import sys

class RIOT():
    def __init__(self, fullname, binary, session_name, tap):
        self.fullname = fullname
        self.binary = binary
        self.session_name = session_name
        self.tap = tap
        # XXX: tmux hack
        self.pid = self.fullname

        self.logger = logging.getLogger("")

    def create(self):
        # TODO: replace tmux sessions by forking riot native to background
        self.logger.info("Start the RIOT: %s: %s" % (self.binary, self.tap))
        window_name = self.fullname 
        tmux_has_session = ["tmux has-session -t %s" % self.session_name]
        tmux_new_session = ["tmux new-session -s %s -n %s -d '%s %s'" % (self.session_name, window_name, self.binary, self.tap)]
        tmux_new_window = ["tmux new-window -t %s:+1 -n %s -P -F'#{window_index}' '%s %s'" % (self.session_name, window_name, self.binary, self.tap)]

        if subprocess.call(tmux_has_session, stderr=subprocess.PIPE, shell=True):
            self.logger.debug("%s not existing, creating new one..." % self.session_name)
            if subprocess.call(tmux_new_session, stderr=subprocess.PIPE, shell=True):
                self.logger.error("creating tmux session failed")
                sys.exit(1)
            else:
                # XXX: misusing self.pid for tmux window number
                self.pid = window_name
        else:
            try:
                output = subprocess.check_output(tmux_new_window, stderr=subprocess.PIPE, shell=True)
                self.pid = window_name
            except subprocess.CalledProcessError:
                self.logger.error("creating tmux window failed")
                sys.exit(1)
        if subprocess.call(tmux_has_session, stderr=subprocess.PIPE, shell=True):
            self.logger.debug("%s does still not exist: something went wrong" % self.session_name)
            sys.exit(1)
        self.is_active = True

    def destroy(self):
        # TODO: replace tmux commands by killing the RIOT process
        self.logger.info("Kill the RIOT: %s (%s)" % (self.binary, self.pid))
        tmux_kill_session = ["tmux kill-window -t %s:%s" % (self.session_name, self.pid)]
        if subprocess.call(tmux_kill_session, stderr=subprocess.PIPE, shell=True):
            self.logger.debug(tmux_kill_session)
            self.logger.error("killing tmux session failed")
            sys.exit(1)
        self.is_active = False

    def isActive(self):
        tmux_list_windows = ['tmux list-windows -t %s -F "#{window_name}"' % self.session_name]
        try:
            output = subprocess.check_output(tmux_list_windows, stderr=subprocess.PIPE, shell=True)
            if (self.fullname in output):
                return True
            else:
                return False
        except subprocess.CalledProcessError:
            self.logger.debug("tmux not running")
            return False

    def exist(self):
        return True

    def __str__(self):
        return "%s %s" % (self.binary, self.tap)
