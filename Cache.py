# browser local cache
class Cache:
    # cache could have been a dict, but I used a separate class for the actual records inside the cache
    def __init__(self):
        self.cache = []

    def getCache(self):
        return self.cache

    # method to search for an item, remove it if found, and append it to the cache list
    def flushCacheRecord(self, cacheRecord):
        for record in self.cache:
            hostname = record.getHostname()
            ip = record.getIP()
            if cacheRecord.getHostname() == hostname or cacheRecord.getIP() == ip:
                self.cache.remove(record)
        self.cache.append(cacheRecord)

    # same method as moments ago but this is used only to refresh the cache when update responses are sent :P
    # did not find a better way, although surely there is one
    def updateCacheRecord(self, cacheRecord):
        for record in self.cache:
            hostname = record.getHostname()
            ip = record.getIP()
            if cacheRecord.getHostname() == hostname or cacheRecord.getIP() == ip:
                self.cache.remove(record)
                self.cache.append(cacheRecord)

    # method to retrieve the ip of a record if it is stored in the cache
    def searchCacheByHostname(self, hostname):
        for cache_record in self.cache:
            if cache_record.getHostname() == hostname:
                return cache_record.getIP()
        return False
