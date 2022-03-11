#!../venv/bin/python

from frontend.routes import webapp
webapp.run('0.0.0.0',5000,debug=True,threaded=True)

