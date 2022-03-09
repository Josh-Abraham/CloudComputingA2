from memcache_app import config, webapp, memcache, constants, startup
from flask import request
import json
global new_cache

startup.call_ready_request()

@webapp.route('/put', methods = ['POST'])
def put():
    """ Put request to add key to memecache

        Parameters:
            request (Request): key and base64 image

        Return:
            response (JSON): "OK" or "ERROR"
    """
    req_json = request.get_json(force=True)
    key, value = list(req_json.items())[0]
    config.memcache_obj.pushitem(key, value)
    return get_response(True)

@webapp.route('/clear', methods = ['GET', 'POST'])
def clear():
    """ Clear cache values

        Return:
            response (JSON): "OK"
    """
    config.memcache_obj.clear_cache()
    return get_response(True)

@webapp.route('/get', methods = ['POST'])
def get():
    """ Get key from cache

        Parameters:
            request (Request): key

        Return:
            response: "OK" or "Unknown Key"
    """
    req_json = request.get_json(force=True)
    key = req_json["keyReq"]
    response=config.memcache_obj.getitem(key)
    if response==None:
        return "Unknown key"
        #check db and put into memcache
    else:
        return response

@webapp.route('/test/<key>/<value>')
def test(key,value):
    response=config.memcache_obj.pushitem(key,value)
    return get_response(response)

@webapp.route('/invalidate', methods = ['POST'])
def invalidate():
    """ Invalidate key in cache

        Parameters:
            request (Request): key

        Return:
            response (JSON): "OK"
    """
    req_json = request.get_json(force=True)
    config.memcache_obj.invalidate(req_json["key"])
    return get_response(True)

def create_new_cache(replacement_policy, capacity):
    '''A new cache object is created and the previous cache
    values are added into it.
        Parameters:
            replacement_policy: string
            capacity: integer

        Return:
            True
    '''
    global new_cache
    print("capacity is:", capacity)
    if (replacement_policy == constants.LRU):
        new_cache = memcache.LRUMemCache(capacity)
    else:
        new_cache = memcache.RRMemCache(capacity)
    new_cache.maximum_size = capacity*pow(2,20)
    new_cache.replace_policy = replacement_policy
    data = config.memcache_obj._Cache__data
    for key,value in data.items():
        new_cache.pushitem(key, value)
    new_cache.access_count = config.memcache_obj.access_count
    new_cache.hit = config.memcache_obj.hit
    new_cache.miss = config.memcache_obj.miss
    return True

def get_response(input=False):
    if input:
        response = webapp.response_class(
            response=json.dumps("OK"),
            status=200,
            mimetype='application/json'
        )
    else:
        response = webapp.response_class(
            response=json.dumps("Bad Request"),
            status=400,
            mimetype='application/json'
        )

    return response

def get_response_no_key():
    response = webapp.response_class(
        response=json.dumps("Unknown key"),
        status=400,
        mimetype='application/json'
    )

    return response
