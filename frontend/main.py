
from glob import glob
from flask import Flask, render_template, g, request, redirect, url_for
from frontend.key_store import image_routes
from frontend.test_api import api_routes
import json

# Flask Blueprint Setup
webapp = Flask(__name__)
webapp.register_blueprint(image_routes)
webapp.register_blueprint(api_routes)

global pool_notification
pool_notification = ""

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
    global pool_notification
    return render_template("home.html", pool_notification=pool_notification)

@webapp.route("/show_notification", methods=['POST'])
def show_notification():
    global pool_notification
    pool_notification = request.get_json(force=True)
    response = webapp.response_class(
            response=json.dumps("OK"),
            status=200,
            mimetype='application/json'
        )
    return response

@webapp.route("/clear_notification", methods=['POST'])
def clear_notification():
    global pool_notification
    pool_notification = ""
    return redirect(redirect_url())

def redirect_url(default='index'):
    return request.args.get('next') or \
           request.referrer or \
           url_for(default)