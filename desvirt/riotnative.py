

import logging
import subprocess
import sys
import socket
import re
import os

reserved_ports = []

def get_free_tcp_port(start_port=4711,logger=None):
    for i in range(1000):
        if ((start_port + i) not in reserved_ports):
            try:
                # AF_INET and SOCK_STREAM are default
                s = socket.socket()
                s.bind(('', start_port + i))
                s.close()
                logger.debug("Found free port at %d" % (start_port + i))
                reserved_ports.append(start_port + i)
                return (start_port + i)
            except socket.error as oe:
                if (oe.errno == 98):
                    logger.debug("Port %d is already in use, try another one" % (start_port + i))
                else:
                    logger.error("Fatal error while searching a free TCP port: %s" % str(oe))
                    sys.exit(1)


class RIOT():

    def __init__(self, fullname, binary, tcp_port, session_name, tap):
        self.fullname = fullname
        self.binary = binary
        self.tcp_port = tcp_port
        self.session_name = session_name
        self.tap = tap
        self.pid = None

        self.logger = logging.getLogger("")
        self.routers_file = "./ports.list"

    def create(self):
        if self.tcp_port:
            port_number = int(self.tcp_port)
        else:
            port_number = get_free_tcp_port(logger=self.logger)
        start_riot = "socat EXEC:'%s %s',end-close,stderr,pty TCP-L:%d,reuseaddr,fork" \
                     % (self.binary, self.tap, port_number)
        self.logger.info("Start the RIOT: %s" % start_riot)
        try:
            proc = subprocess.Popen(start_riot, shell=True)
            self.pid = proc.pid
            self.logger.info("PID: %d" % self.pid)

            with open(self.routers_file, "a") as f:
                position = self.tap.split("_", 1)[1] #a1..e7
                x = ord(position[0]) - ord('a') + 1 #1..5
                if (len(position) > 1):
                    y = int(position[1]) #1..5
                    print(str(x) + "," + str(y) + "," + str(port_number), file=f)
                else:
                    print(str(x) + "," + str(port_number), file=f)

        except subprocess.CalledProcessError:
            self.logger.error("creating RIOT native process failed")
            sys.exit(1)

        self.is_active = True

    def destroy(self):
        self.logger.info("Kill the RIOT: %s (%s)" % (self.binary, self.pid))
        kill_string = ['pkill -f -9 "%s %s"' % (self.binary, self.tap)]
        if subprocess.call(kill_string, stderr=subprocess.PIPE, shell=True):
            self.logger.error("killing RIOT native process failed")
        self.is_active = False

    def isActive(self):
        if (not self.pid):
            return False
        find_process = ['ps h %d' % (self.pid)]
        try:
            output = subprocess.check_output(find_process, stderr=subprocess.PIPE, shell=True)
            if (len(output)):
                return True
            else:
                return False
        except subprocess.CalledProcessError:
            self.logger.debug("Process not found")
            return False

    def exist(self):
        return True

    def __str__(self):
        return "%s %s" % (self.binary, self.tap)
