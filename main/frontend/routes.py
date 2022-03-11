
from flask import Flask, g
import os
from frontend.cache import cache_routes
from frontend.image_utils import routes

# Flask Setup



webapp = Flask(__name__)
webapp.register_blueprint(routes)
webapp.register_blueprint(cache_routes)


@webapp.teardown_appcontext
def teardown_db(exception):
    """ Tear down database connect when shutting down
    """
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()