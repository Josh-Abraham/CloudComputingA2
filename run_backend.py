#!../venv/bin/python

from manager_server import webapp
webapp.run('0.0.0.0',5002,debug=True,threaded=True, use_reloader=False)

