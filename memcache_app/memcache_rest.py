from memcache_app import config, webapp, memcache, constants, startup
from flask import request
import json, datetime
global new_cache

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

@webapp.route('/refreshConfiguration', methods = ['POST'])
def refresh_configs():
    """ Refresh configuration with new parameters
        Parameters:
            request (Request): Capacity and replacement policy
        Return:
            response (JSON): "OK"
    """
    print("In the Route")
    cache_params = request.get_json(force=True)
    if not cache_params == None:
        capacity = cache_params['max_capacity']
        replacement_policy = cache_params['replacement_policy']
        create_new_cache(replacement_policy, capacity)
        config.memcache_obj = new_cache
        return get_response(True)
    return None

@webapp.route('/getStatistics', methods = ['GET'])
def get_statistics():
    statistics = {
        'size': config.memcache_obj.current_size, 
        'access_count': config.memcache_obj.access_count,
        'miss_rate': config.memcache_obj.miss,
        'key_count': config.memcache_obj.currsize,
        'hit_rate': config.memcache_obj.hit
    }
    response = webapp.response_class(
            response=json.dumps(statistics),
            status=200,
            mimetype='application/json'
    )
    return response

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

def startup_app():
    print("Setting Params on start")
    cache_params = json.loads(startup.call_ready_request())
    capacity = cache_params['max_capacity']
    replacement_policy = cache_params['replacement_policy']
    create_new_cache(replacement_policy, capacity)
    config.memcache_obj = new_cache

startup_app()