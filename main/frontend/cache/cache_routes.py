from flask import Blueprint
import requests, time, datetime
from flask import render_template, request

cache_routes = Blueprint("cache_routes", __name__)

# @cache_routes.route('/memcache_manager', methods=['GET'])
# def memcache_manager():
#     global cache_config



@cache_routes.route('/set_cache_params', methods = ['GET','POST'])
def memcache_params():
    """ Memcache Paremeters has 3 unique functionailities depending on case
    GET: Fetch the database configurations for the memcache
    POST: Clear button hit will clear the cache
    POST: Set new parameters, pass them into the database and format for the UI
    """
    global cache_host
    cache_params = None
    if not cache_params == None:
        update_time = time.ctime(cache_params[1])
        capacity = cache_params[2]
        replacement_policy = cache_params[3]
    else:
        # Error catching case, will set to 0 values so it startups gracefully
        update_time = time.ctime(time.time())
        capacity = 0
        replacement_policy = "Least Recently Used"

    # Go from Epoch time to formatted date-time object
    date = datetime.datetime.strptime(update_time, "%a %b %d %H:%M:%S %Y")
    date.strftime("YYYY/MM/DD HH:mm:ss (%Y%m%d %H:%M:%S)")

    if request.method == 'POST':

        if not request.form.get("clear_cache") == None:
            # Clear button is hit, will clear the current cache
            requests.post(cache_host + '/clear')
            return render_template('memcache_manager.html', capacity=capacity, replacement_policy=replacement_policy, update_time=date, status="CLEAR")
        else:
            # Check new cache paramters
            new_cap = request.form.get('capacity')
            if new_cap.isdigit() and int(new_cap) <= 500:
                new_policy = request.form.get('replacement_policy')
                new_time = set_cache_params(new_cap, new_policy)
                if not new_time == None:
                    new_time = datetime.datetime.strptime(time.ctime(new_time), "%a %b %d %H:%M:%S %Y")
                    new_time.strftime("YYYY/MM/DD HH:mm:ss (%Y%m%d %H:%M:%S)")
                    resp = requests.post(cache_host + '/refreshConfiguration')
                    if resp.json() == 'OK':
                        return render_template('memcache_manager.html', capacity=new_cap, replacement_policy=new_policy, update_time=new_time, status="FALSE")
            # On error, reset to old params. Not set in the DB, so only a UI refresh is needed
            return render_template('memcache_manager.html', capacity=capacity, replacement_policy=replacement_policy, update_time=date, status="TRUE")
    return render_template('memcache_manager.html', capacity=capacity, replacement_policy=replacement_policy, update_time=date)


def set_cache_params(new_cap, new_policy):
    return None