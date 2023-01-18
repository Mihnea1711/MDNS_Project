transport_proto = "_udp"
domain_name = "local"
PORT = 5353
TTL = 120   # default time to live


# class to store data (service, protocol, domain, target, etc) about a service
class SRV_RECORD:
    def __init__(self, service, target):
        self.service = service if service[0] == "_" else f"_{service}"
        self.target = target            # this should be the hostname of the service
        self.ttl = TTL
        self.proto = transport_proto    # implicit "_udp"
        self.domain = domain_name       # implicit .local
        self.port = PORT                # implicit 5353
        self.rclass = "IN"              # implicitly means lookup in the internet

    def getService(self):
        return self.service

    def setService(self, service):
        self.service = service if service[0] == "_" else f"_{service}"

    def getTTL(self):
        return self.ttl

    def setTTL(self, ttl):
        if not ttl.isnumeric():
            return False, "TTL should be a number.\n"
        if not int(ttl) > 0:
            return False, "TTL should be positive.\n"
        self.ttl = int(ttl)
        return True, "TTL looks good.\n"

    def getTarget(self):
        return self.target

    def setTarget(self, target):
        self.target = target

    def getProto(self):
        return self.proto

    def getDomain(self):
        return self.domain

    def __str__(self):
        return f"{self.service}.{self.proto}.{domain_name} {self.ttl} {self.rclass} {PORT} {self.target}.{domain_name}"
