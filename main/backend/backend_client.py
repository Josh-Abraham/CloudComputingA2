from backend import webapp
from flask import request
from backend import ec2_lifecycle
import json
global new_cache
global memcache_pool
memcache_pool = {
    "i-04064013ac1862adf": None
}


@webapp.route('/', methods = ['GET'])
def main():
    return get_response(True)

@webapp.route('/readyRequest', methods = ['POST'])
def ready_request():
    global memcache_pool
    req_json = request.get_json(force=True)
    memcache_pool[req_json['instance_id']] = req_json['ip_address']
    print('New Host address')
    print(memcache_pool['i-04064013ac1862adf'])
    return get_response(True)

@webapp.route('/startInstance', methods = ['POST', 'GET'])
def start_instance():
    ec2_lifecycle.startup('i-04064013ac1862adf')
    return get_response(True)

@webapp.route('/stopInstance', methods = ['POST', 'GET'])
def stop_instance():
    global memcache_pool
    memcache_pool['i-04064013ac1862adf'] = None
    ec2_lifecycle.shutdown('i-04064013ac1862adf')
    return get_response(True)


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
