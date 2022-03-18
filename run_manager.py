#!../venv/bin/python

from manager_client.main import webapp
webapp.run('0.0.0.0',5001,debug=True,threaded=True)
