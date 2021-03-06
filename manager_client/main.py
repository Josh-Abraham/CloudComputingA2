
from flask import Flask, render_template, g
from manager_client.cache import cache_routes
from manager_client.statistics import stats_routes

# Flask Blueprint Setup
webapp = Flask(__name__)
webapp.register_blueprint(cache_routes)
webapp.register_blueprint(stats_routes)

# Core Routes
@webapp.teardown_appcontext
def teardown_db(exception):
    """ Tear down database connect when shutting down
    """
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

@webapp.errorhandler(404)
def not_found(e):
    """ Error template goes back to home
    """
    return render_template("home.html")

@webapp.route('/')
@webapp.route('/home')
def home():
    """ Main route, as well as default location for 404s
    """
    return render_template("home.html")
