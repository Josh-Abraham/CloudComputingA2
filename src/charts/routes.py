from flask import render_template
from charts import webapp

@webapp.route('/')
@webapp.route('/home')
def home():
    """ Main route, as well as default location for 404s
    """
    return render_template("index.html")
