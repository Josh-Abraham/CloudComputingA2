from flask import Blueprint, render_template
import json
from manager_client.statistics.plot_utils import *
from manager_client.statistics.stats_calc import get_stats_logs

stats_routes = Blueprint("stats_routes", __name__)

@stats_routes.route('/cache_stats')
def new_stats():
    current_stats = get_stats_logs()
    current_stats = json.dumps(current_stats)
    return render_template('chart.html', stats_data=current_stats)
