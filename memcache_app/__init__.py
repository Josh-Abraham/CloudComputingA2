from flask import Flask
from memcache_app import memcache
import requests
from memcache_app import config
webapp = Flask(__name__)

''' Default Type is LRU and default size is 2 MB'''
config.memcache_obj = memcache.LRUMemCache(2)

from memcache_app import memcache_rest