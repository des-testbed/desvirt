import logging

class RIOT():
    def __init__(self, binary, pid, tap):
        self.binary = binary
        self.pid = pid
        self.tap = tap

        self.is_active = False

        self.logger = logging.getLogger("")

    def create(self):
        # TODO: execute RIOT native here
        self.logger.info("Start the RIOT: %s: %s" % (self.binary, self.tap))
        self.is_active = True

    def destroy(self):
        # TODO: kill RIOT native
        self.logger.info("Kill the RIOT: %s (%s)" % (self.binary, self.pid))
        self.is_active = False

    def isActive(self):
        return self.is_active
