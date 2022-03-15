#!../venv/bin/python

from main.frontend.main import webapp
webapp.run('0.0.0.0',5000,debug=False,threaded=True)
