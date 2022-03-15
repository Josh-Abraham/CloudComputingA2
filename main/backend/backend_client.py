from multiprocessing import pool
from backend import webapp, memcache_pool
from flask import request
from backend import ec2_lifecycle
import json, time, requests

STATES = ['Starting', 'Stopping']

cache_params = {
    'max_capacity': 2,
    'replacement_policy': 'Least Recently Used',
    'update_time': time.time()
}

pool_params = {
    'mode': 'manual',
    'settings': {
        'size': 0
    }
}

@webapp.before_first_request
def setup_pool():
    """ Set Pool configuration
    """
    startup_count = ec2_lifecycle.set_pool_status()
    if startup_count == 0:
        start_instance()


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
    print('New Host address:' + memcache_pool[req_json['instance_id']])

    return get_cache_response()

@webapp.route('/startInstance', methods = ['POST', 'GET'])
def start_instance():
    """ Code to start an EC2 instance
    """
    id = get_next_node()
    if not id == None:
        print('Starting up ' + id)
        memcache_pool[id] = 'Starting'
        ec2_lifecycle.startup(id)
    
    return get_response(True)

@webapp.route('/stopInstance', methods = ['POST', 'GET'])
def stop_instance():
    """ Code to stop an EC2 instance
    """
    global memcache_pool
    id = get_active_node()
    if not id == None:
        print('Shutting down ' + id)
        memcache_pool[id] = 'Stopping'
        ec2_lifecycle.shutdown(id)
    return get_response(True)

@webapp.route('/getCacheInfo', methods = ['GET'])
def get_cache_info():
    """ Return all cache info (params and active instances)
    to the FE flask
    """
    global memcache_pool, cache_params, pool_params
    print(memcache_pool)
    response = {
                'memcache_pool': memcache_pool,
                'cache_params': cache_params,
                'pool_params': pool_params
            }
    
    return webapp.response_class(
            response = json.dumps(response),
            status=200,
            mimetype='application/json'
        )

@webapp.route('/refreshConfiguration', methods = ['POST'])
def refresh_configuration():
    global cache_params, memcache_pool
    """ Set cache params
    """
    cache_params = request.get_json(force=True)
    print(cache_params)
    for host in memcache_pool:
        address_ip = memcache_pool[host]
        if not address_ip == None and not address_ip in STATES: 
            # If an address is starting up, it will be set once it is ready
            address = 'http://' + str(address_ip) + ':5000/refreshConfiguration'
            res = requests.post(address, json=cache_params)

    return webapp.response_class(
            response = json.dumps("OK"),
            status=200,
            mimetype='application/json'
        )

@webapp.route('/clear_cache_pool', methods = ['POST'])
def clear_cache_pool():
    """ Clear cache content
    """
    for host in memcache_pool:
        address_ip = memcache_pool[host]
        print('IP ' + address_ip)
        if not address_ip == None and not address_ip in STATES:
            # Only need to clear active ports
            address = 'http://' + str(address_ip) + ':5000/clear'
            res = requests.post(address)

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

def get_next_node():
    """ Used to find the next available node to startup
    """
    global memcache_pool
    for id, ip in memcache_pool.items():
        if ip == None:
            return id
    return None

def get_active_node():
    """ Used to find the next available node to shutdown
    Goes in reverse order so you aren't always shutting down the node you just started
    """
    global memcache_pool
    for id, ip in reversed(memcache_pool.items()):
        if not ip == None and not ip == 'Stopping':
            return id
    return None

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

def get_cache_response():
    response = webapp.response_class(
        response=json.dumps(cache_params),
        status=200,
        mimetype='application/json'
    )
    
    return response