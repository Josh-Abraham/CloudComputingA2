#!../venv/bin/python

from charts import webapp
webapp.run('0.0.0.0',5000,debug=True,threaded=True)
#webapp.run('0.0.0.0',5000)

