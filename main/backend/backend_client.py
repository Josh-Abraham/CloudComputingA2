from backend import webapp
from flask import request
# from backend import ec2_lifecycle
import json, time

cache_params = {
    'max_capacity': 2,
    'replacement_policy': 'Least Recently Used',
    'update_time': time.time()
}

memcache_pool = {
    "i-04064013ac1862adf": "1234"
}


@webapp.before_first_request
def set_cache_db_settings():
    """ Set Cache Parameters
    """
    #TODO: on startup of BE, set cache params of all active nodes
    #TODO: Also set active EC2 instance list


@webapp.route('/', methods = ['GET'])
def main():
    return get_response(True)

@webapp.route('/readyRequest', methods = ['POST'])
def ready_request():
    """ Ready Request sent from memcache pool to BE
    Needs to be forwarded to the FE Flask on ready
    """
    global memcache_pool
    req_json = request.get_json(force=True)
    memcache_pool[req_json['instance_id']] = req_json['ip_address']
    print('New Host address')
    print(memcache_pool['i-04064013ac1862adf'])
    return get_response(True)

# @webapp.route('/startInstance', methods = ['POST', 'GET'])
# def start_instance():
#     """ Code to start an EC2 instance
#     TODO: Remve hard coded instance for next available
#     """
#     ec2_lifecycle.startup('i-04064013ac1862adf')
#     return get_response(True)

# @webapp.route('/stopInstance', methods = ['POST', 'GET'])
# def stop_instance():
#     """ Code to stop an EC2 instance
#     TODO: Remve hard coded instance for next available
#     """
#     global memcache_pool
#     memcache_pool['i-04064013ac1862adf'] = None
#     ec2_lifecycle.shutdown('i-04064013ac1862adf')
#     return get_response(True)

@webapp.route('/getCacheInfo', methods = ['GET'])
def get_cache_info():
    """ Return all cache info (params and active instances)
    to the FE flask
    """
    global memcache_pool, cache_params
    response = {
                'memcache_pool': memcache_pool,
                'cache_params': cache_params
            }
    
    return webapp.response_class(
            response = json.dumps(response),
            status=200,
            mimetype='application/json'
        )

@webapp.route('/refreshConfiguration', methods = ['POST'])
def refresh_configuration():
    global cache_params
    """ Set cache params
    """
    cache_params = request.get_json(force=True)
    print(cache_params)
    # TODO: Need to call refresh config on cache pool
    
    return webapp.response_class(
            response = json.dumps("OK"),
            status=200,
            mimetype='application/json'
        )

@webapp.route('/clear_cache_pool', methods = ['POST'])
def clear_cache_pool():
    # TODO: Call clear on cache pool
    return webapp.response_class(
            response = json.dumps("OK"),
            status=200,
            mimetype='application/json'
        )

@webapp.route('/clear_data', methods = ['POST'])
def clear_data():
    # TODO: Call clear on S3 Data
    return webapp.response_class(
            response = json.dumps("OK"),
            status=200,
            mimetype='application/json'
        )

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
