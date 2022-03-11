#!../venv/bin/python
from memcache_app import webapp


webapp.run('0.0.0.0',5001,debug=True,threaded=True)

#webapp.run('0.0.0.0',5001)

