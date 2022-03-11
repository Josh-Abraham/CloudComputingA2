#!../venv/bin/python

from frontend.main import webapp
webapp.run('0.0.0.0',5000,debug=False,threaded=True)