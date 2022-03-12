from ipaddress import ip_address
from tkinter.messagebox import NO
from types import NoneType
from flask import Blueprint
import requests, time, datetime
from flask import render_template, request

cache_routes = Blueprint("cache_routes", __name__)
backend_app = 'http://localhost:5001'


@cache_routes.route('/memcache_manager', methods=['GET'])
def memcache_manager():
    capacity, replacement_policy, update_time, memcache_pool = format_cache_settings()
    return render_template('memcache_manager.html',
        capacity=capacity,
        replacement_policy=replacement_policy,
        update_time=update_time,
        memcache_pool=memcache_pool)


@cache_routes.route('/set_cache_params', methods = ['GET', 'POST'])
def memcache_params():
    global backend_app
    new_cap = request.form.get('capacity')
    if (not type(new_cap) == NoneType) and  new_cap.isdigit() and int(new_cap) <= 500:
        new_policy = request.form.get('replacement_policy')
        new_time = time.time()
        req = {
            'max_capacity': new_cap, 
            'replacement_policy': new_policy, 
            'update_time': new_time
        }
        resp = requests.post(backend_app + '/refreshConfiguration', json=req)
        capacity, replacement_policy, update_time, memcache_pool = format_cache_settings()
        if resp.json() == 'OK':
            return render_template('memcache_manager.html',
            capacity=capacity,
            replacement_policy=replacement_policy,
            update_time=update_time,
            memcache_pool=memcache_pool)
    # On error, reset to old params
    capacity, replacement_policy, update_time, memcache_pool = format_cache_settings()
    return render_template('memcache_manager.html',
            capacity=capacity,
            replacement_policy=replacement_policy,
            update_time=update_time,
            memcache_pool=memcache_pool,
            status="TRUE")

@cache_routes.route('/clear_cache', methods=['GET', 'POST'])
def clear_cache():
    global backend_app
    res = requests.get(backend_app + '/clear_cache_pool')
    capacity, replacement_policy, update_time, memcache_pool = format_cache_settings()
    return render_template('memcache_manager.html',
        capacity=capacity,
        replacement_policy=replacement_policy,
        update_time=update_time,
        memcache_pool=memcache_pool)

@cache_routes.route('/clear_data', methods=['GET', 'POST'])
def clear_data():
    global backend_app
    res = requests.get(backend_app + '/clear_data')
    capacity, replacement_policy, update_time, memcache_pool = format_cache_settings()
    return render_template('memcache_manager.html',
        capacity=capacity,
        replacement_policy=replacement_policy,
        update_time=update_time,
        memcache_pool=memcache_pool)

def format_cache_settings():
    global backend_app
    res = requests.get(backend_app + '/getCacheInfo')
    memcache_pool = res.json()['memcache_pool']
    capacity = res.json()['cache_params']['max_capacity']
    replacement_policy = res.json()['cache_params']['replacement_policy']
    update_time = time.ctime(res.json()['cache_params']['update_time'])

    i = 1
    pool_data = []
    for id, ip_address in memcache_pool.items():
        if not ip_address == None:
            pool_data.append(
                { 'value': i, 'name': 'Node ' + str(i) }
            )
            i += 1
    return capacity, replacement_policy, update_time, pool_data