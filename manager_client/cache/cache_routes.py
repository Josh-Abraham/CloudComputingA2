
from flask import Blueprint
import requests, time
from flask import render_template, request, redirect
from frontend.db_connection import get_db

cache_routes = Blueprint("cache_routes", __name__)
backend_app = 'http://localhost:5002'


@cache_routes.route('/memcache_manager', methods=['GET'])
def memcache_manager():
    print("test Connection")
    cnx = get_db()
    capacity, replacement_policy, update_time, memcache_pool, node_data, pool_params = format_cache_settings()
    return render_template('memcache_manager.html',
        capacity=capacity,
        replacement_policy=replacement_policy,
        update_time=update_time,
        memcache_pool=memcache_pool,
        pool_params=pool_params,
        node_data=node_data)


@cache_routes.route('/set_cache_params', methods = ['GET', 'POST'])
def memcache_params():
    global backend_app
    if request.method == 'POST':
        new_cap = request.form.get('capacity')
        if new_cap.isdigit() and int(new_cap) <= 500:
            new_policy = request.form.get('replacement_policy')
            new_time = time.time()
            req = {
                'max_capacity': new_cap, 
                'replacement_policy': new_policy, 
                'update_time': new_time
            }
            resp = requests.post(backend_app + '/refreshConfiguration', json=req)
            capacity, replacement_policy, update_time, memcache_pool, node_data, pool_params = format_cache_settings()
            if resp.json() == 'OK':
                return render_template('memcache_manager.html',
                capacity=capacity,
                replacement_policy=replacement_policy,
                update_time=update_time,
                memcache_pool=memcache_pool,
                pool_params=pool_params,
                node_data=node_data)
             
        # On error, reset to old params
        capacity, replacement_policy, update_time, memcache_pool, node_data, pool_params = format_cache_settings()
        return render_template('memcache_manager.html',
                capacity=capacity,
                replacement_policy=replacement_policy,
                update_time=update_time,
                memcache_pool=memcache_pool,
                pool_params=pool_params,
                node_data=node_data,
                status="TRUE")
        
    # On GET
    capacity, replacement_policy, update_time, memcache_pool, node_data, pool_params = format_cache_settings()
    return render_template('memcache_manager.html',
            capacity=capacity,
            replacement_policy=replacement_policy,
            update_time=update_time,
            memcache_pool=memcache_pool,
            pool_params=pool_params,
            node_data=node_data)
    
    

@cache_routes.route('/clear_cache', methods=['GET', 'POST'])
def clear_cache():
    global backend_app
    if request.method == 'POST':
        res = requests.post(backend_app + '/clear_cache_pool')
    capacity, replacement_policy, update_time, memcache_pool, node_data, pool_params = format_cache_settings()
    return render_template('memcache_manager.html',
        capacity=capacity,
        replacement_policy=replacement_policy,
        update_time=update_time,
        memcache_pool=memcache_pool,
        pool_params=pool_params,
        node_data=node_data)

@cache_routes.route('/clear_data', methods=['GET', 'POST'])
def clear_data():
    global backend_app
    if request.method == 'POST':
        res = requests.get(backend_app + '/clear_data')
    capacity, replacement_policy, update_time, memcache_pool, node_data, pool_params = format_cache_settings()
    return render_template('memcache_manager.html',
        capacity=capacity,
        replacement_policy=replacement_policy,
        update_time=update_time,
        memcache_pool=memcache_pool,
        pool_params=pool_params,
        node_data=node_data)


@cache_routes.route('/set_pool_config', methods=['GET', 'POST'])
def set_pool_config():
    global backend_app
    if request.method == 'POST':
        if request.form.get("mode") == 'Manual Mode':
            manual_update_pool(request.form.get("pool-button"))
            
        else:
            max_miss_rate = request.form.get("maxMiss")
            min_miss_rate = request.form.get("minMiss")
            exp_ratio = request.form.get("expRatio")
            shrink_ratio = request.form.get("shrinkRatio")

            cnx = get_db()
            cursor = cnx.cursor(dictionary=True)
            query_add = ''' INSERT INTO cache_policy (max_miss_rate, min_miss_rate, exp_ratio, shrink_ratio) VALUES (%s,%s,%s,%s)'''
            cursor.execute(query_add,(max_miss_rate, min_miss_rate, exp_ratio, shrink_ratio))
            cnx.commit()
            cnx.close()

            
            print(request.form.get("mode"))
        
        
    capacity, replacement_policy, update_time, memcache_pool, node_data, pool_params = format_cache_settings()
    return render_template('memcache_manager.html',
        capacity=capacity,
        replacement_policy=replacement_policy,
        update_time=update_time,
        memcache_pool=memcache_pool,
        pool_params=pool_params,
        node_data=node_data)


def format_cache_settings():
    global backend_app
    res = requests.get(backend_app + '/getCacheInfo')
    memcache_pool = res.json()['memcache_pool']
    capacity = res.json()['cache_params']['max_capacity']
    replacement_policy = res.json()['cache_params']['replacement_policy']
    update_time = time.ctime(res.json()['cache_params']['update_time'])
    pool_params = res.json()['pool_params']

    i = 1
    stopping_nodes = 0
    starting_nodes = 0
    active_nodes = 0
    pool_data = []
    for id, ip_address in memcache_pool.items():
        if not ip_address == None:
            if ip_address == 'Starting' or ip_address == 'Stopping':
                pool_data.append(
                    { 'value': 1, 'name': 'Node ' + str(i) + ' ' + ip_address }
                )

            else:
                pool_data.append(
                    { 'value': 1, 'name': 'Node ' + str(i) }
                )
            i += 1
            
            if ip_address == 'Stopping':
                stopping_nodes += 1
            elif ip_address == 'Starting':
                starting_nodes += 1
            else:
                active_nodes += 1

    node_data = {
        'active': active_nodes,
        'stopping': stopping_nodes,
        'starting': starting_nodes
    }
    return capacity, replacement_policy, update_time, pool_data, node_data, pool_params

@cache_routes.route('/navigate')
def navigate():
	hostname = request.headers.get('Host').split(':')[0]
	print(hostname)
	return redirect('http://'+hostname + ':5000')


def manual_update_pool(cmd):
    if cmd == 'increase':
        resp = requests.post(backend_app + '/startInstance')
    else:
        resp = requests.post(backend_app + '/stopInstance')
