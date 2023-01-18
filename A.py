class A_RECORD:
    def __init__(self, hostname, ip):
        self.hostname = hostname
        self.ip = ip

    def getHostname(self):
        return self.hostname

    def setHostname(self, hostname):
        self.hostname = hostname

    def validateIPAndSave(self, ip):
        flag = True
        message = ""

        if len(ip.split(".")) != 4:
            message += "IP address should have 4 parts separated by dots...\n"
            flag = False

        for adr in ip.split("."):
            if not adr or int(adr) > 255 or int(adr) < 0:
                message += "IP parts should not be higher than 255 and lower than 0\n"
                flag = False
                break

        if flag:
            self.ip = ".".join(list(map(lambda part: part.strip(), ip.split("."))))
            message = "IP looks good.\n"

        return flag, message

    def getIP(self):
        return self.ip

    def setIP(self, ip):
        return self.validateIPAndSave(ip)

    def __str__(self):
        return f"{self.hostname}: {self.ip}"

