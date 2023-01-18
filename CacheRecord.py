import time


# actual record inside the cache
# the default ttl field is the actual value from the GUI
# the ttl field is the one that is decremented
# probably there is a better way to code this, too
class CacheRecord:
    def __init__(self, hostname, ip, ttl):
        self.hostname = hostname
        self.ip = ip
        self.default_ttl = ttl
        self.ttl = ttl
        self.time_created = time.time()

    def __str__(self):
        return f"{self.hostname}: {self.ip} ... {self.ttl}sec"

    def getHostname(self):
        return self.hostname

    def setHostname(self, hostname):
        self.hostname = hostname

    def getIP(self):
        return self.ip

    def setIP(self, ip):
        self.ip = ip

    def getTTL(self):
        return self.ttl

    def setTTL(self, ttl):
        self.ttl = ttl

    def getDefaultTTL(self):
        return self.default_ttl

    def getTimeCreated(self):
        return self.time_created
