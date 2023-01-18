import time
import math


class Cache:
    def __init__(self):
        self.cache = []

    def getCache(self):
        return self.cache

    def flushCacheRecord(self, cacheRecord):
        for record in self.cache:
            hostname = record.getHostname()
            ip = record.getIP()
            if cacheRecord.getHostname() == hostname or cacheRecord.getIP() == ip:
                self.cache.remove(record)
        self.cache.append(cacheRecord)

    def updateCacheRecord(self, cacheRecord):
        for record in self.cache:
            hostname = record.getHostname()
            ip = record.getIP()
            if cacheRecord.getHostname() == hostname or cacheRecord.getIP() == ip:
                self.cache.remove(record)
                self.cache.append(cacheRecord)

    def insertOrUpdateCacheRecord(self, cache_record):
        now = time.time()
        found = False
        for record in self.cache:
            hostname = record.getHostname()
            ip = record.getIP()
            ttl = record.getTTL()
            time_created = record.getTimeCreated()

            # daca e deja in cache
            if cache_record.getHostname() == hostname:
                # setam ttl-ul record-ului cu cel presabilit la creare
                if ip != cache_record.getIP():
                    record.setIP(cache_record.getIP())
                record.setTTL(cache_record.getTTL())
                found = True

            # pentru celelalte, facem update la ttl
            else:
                time_passed = now - time_created
                if math.floor(ttl - time_passed) > 0:
                    # daca nu a expirat facem update la ttl, cu verificare ca timpul ramas sa fie > 0
                    record.setTTL(math.floor(ttl - time_passed))
                else:
                    # daca a expirat, atunci il stergem din lista
                    self.cache.remove(record)
        # la final, dupa ce facem update la toate cele existente, adaugam record-ul daca nu a fost gasit
        if not found:
            self.cache.append(cache_record)

    def searchCacheByHostname(self, hostname):
        for cache_record in self.cache:
            if cache_record.getHostname() == hostname:
                return cache_record.getIP()
        return False
