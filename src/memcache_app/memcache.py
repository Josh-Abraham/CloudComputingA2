from cachetools import LRUCache, RRCache
import random
import time
from memcache_app import constants
from threading import Lock

lock = Lock()
''' 
LRUMemCache is derived from the LRUCache of the cachetools module.
Additional details like the size of cache, hit, miss and access count 
are obtained by over-riding the methods of the super class.
'''
class LRUMemCache(LRUCache):
    def __init__(self, size):
        super().__init__(maxsize = self.MB_to_Bytes(size), getsizeof= None)
        self.replace_policy = constants.LRU
        self.maximum_size = self.MB_to_Bytes(size)
        self.current_size = 0
        self.hit = 0
        self.miss = 0
        self.access_count = 0
    
    def pushitem(self, key, value):
        response = self.__setitem__(key, value)
        self.access_count += 1
        return response

    def updateitem(self, key, new_value):
        if(self.__getitem__(key)):
            current_value = self._Cache__data[key]
            self.current_size -= self.size_base_64(current_value)
            self._Cache__data[key] = new_value
            self.current_size += self.size_base_64(new_value)
            return True
        return False

    def popitem(self):
        if (self.currsize > 0):
            # if(response != None):
            response = super().popitem()
            (key, value) = response
            self.current_size -= self.size_base_64(value)
            print("key popped in LRU is: ", key)
            return(key, value)
        return None

    def getitem(self, key):
        response = self.__getitem__(key)
        if(response == None):
            self.miss += 1
        else:
            self.hit += 1
        self.access_count += 1
        return response

    def invalidate(self, key):
        response = self.__getitem__(key)
        if(response != None):
            (_, value) = response
            super().pop(key)
            self.current_size -= self.size_base_64(value)
            return "OK"
        return None
    
    def clear_cache(self):
        with lock:
            while self.currsize > 0:
                self.popitem()
            self.current_size=0

    def __missing__(self, key): 
        return None

    def __getitem__(self, key):
        response = super().__getitem__(key)
        return response

    def __setitem__(self, key, value):
        size_of_value = self.size_base_64(value)
        if(self.current_size + size_of_value >= self.maximum_size):
            while(self.current_size + size_of_value >= self.maximum_size and self.currsize > 0):
                self.popitem()
        if(key != None and value != None and (self.current_size + size_of_value) <= self.maximum_size):
            super().__setitem__(key, value)
            self.current_size +=  size_of_value
            return True
        return False

    def MB_to_Bytes(self, size):
        return(size*pow(2,20))

    def KB_to_Bytes(self, size):
        return(size*pow(2,10))
    
    def size_base_64(self, value):
        return (3*len(value)/4 - value.count('='))

''' 
RRemCache is derived from the LRUCache of the cachetools module.
Additional details like the size of cache, hit, miss and access count 
are obtained by over-riding the methods of the super class.
'''
class RRMemCache(RRCache):
    def __init__(self, size):
 
        super().__init__(maxsize = self.MB_to_Bytes(size), choice = random.choice, getsizeof= None)
        self.replacement_policy = constants.RR
        self.maximum_size = self.MB_to_Bytes(size)
        self.current_size = 0
        self.hit = 0
        self.miss = 0
        self.access_count = 0
    
    def pushitem(self, key, value):
        response = self.__setitem__(key, value)
        self.access_count += 1
        return response

    def updateitem(self, key, new_value):
        if(self.__getitem__(key)):
            current_value = self._Cache__data[key]
            self.current_size -= self.size_base_64(current_value)
            self._Cache__data[key] = new_value
            self.current_size += self.size_base_64(new_value)
            return True
        return False

    def popitem(self):
        if (self.currsize > 0):
            # if(response != None):
            response = super().popitem()
            (key, value) = response
            self.current_size -= self.size_base_64(value)
            print("key popped is RR: ", key)
            return(key, value)
        return None

    def getitem(self, key):
        response = self.__getitem__(key)
        if(response == None):
            self.miss += 1
        else:
            self.hit += 1
        self.access_count += 1
        return response

    def invalidate(self, key):
        print("entered in validate")
        response = self.__getitem__(key)
        if(response != None):
            (_, value) = response
            super().pop(key)
            self.current_size -= self.size_base_64(value)
            return "OK"
        return None
    
    def clear_cache(self):
        print("entered clear cache")
        with lock:
            while self.currsize > 0:
                self.popitem()
            self.current_size=0
        
    def __missing__(self, key): 
        return None

    def __getitem__(self, key):
        response = super().__getitem__(key)
        return response

    def __setitem__(self, key, value):
        size_of_value = self.size_base_64(value)
        if(self.current_size + size_of_value >= self.maximum_size):
            while(self.current_size + size_of_value >= self.maximum_size and self.currsize > 0):
                self.popitem()
        if(key != None and value != None and (self.current_size + size_of_value) <= self.maximum_size):
            super().__setitem__(key, value)
            self.current_size +=  size_of_value
            return True
        return False

    def MB_to_Bytes(self, size):
        return(size*pow(2,20))

    def KB_to_Bytes(self, size):
        return(size*pow(2,10))
    
    def size_base_64(self, value):
        return (3*len(value)/4 - value.count('='))
