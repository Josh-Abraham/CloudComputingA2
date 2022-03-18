from flask import Blueprint, render_template
from frontend.db_connection import get_db
import datetime, json
from manager_client.statistics.plot_utils import *
from manager_client.statistics.stats_calc import get_stats_logs

stats_routes = Blueprint("stats_routes", __name__)

@stats_routes.route('/cache_stats')
def cache_stats():
    """ Endpoint to show the cache statistics
    Generates and displays the 5 graphs/plots pertaining to the statistics
    of the memcache for the past 10 minutes.
    Display image as Base64
    """
    cnx = get_db()
    cursor = cnx.cursor(dictionary=True)
    stop_time = datetime.datetime.now()
    start_time = stop_time - datetime.timedelta(minutes=10)
    query = '''SELECT * FROM cache_stats cs WHERE cs.created_at > %s and cs.created_at < %s'''
    cursor.execute(query, (start_time, stop_time))
    rows = cursor.fetchall()
    cnx.close()

    (x_data, y_data) = prepare_data(rows)
    image_map = {}
    for k,v in y_data.items():
        image_map[k] = plot_graphs(x_data['x-axis'], v, k)

    return render_template('cache_stats.html', cache_count_plot = image_map['cache_count'],
                            request_plot = image_map['request_count'], cache_size_plot = image_map['cache_size'],
                             hit_plot = image_map['hit'], miss_plot = image_map['miss'])

@stats_routes.route('/new_stats')
def new_stats():
    current_stats = get_stats_logs()
    current_stats = json.dumps(current_stats)
    return render_template('chart.html', stats_data=current_stats)
