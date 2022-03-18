from flask import Flask
import threading
webapp = Flask(__name__)
memcache_pool = {
    "i-04064013ac1862adf": None,
    "i-0360438eeb0ed4afc": None
}
from manager_server import backend_client
from manager_server.statistics_server import thread_stats

th = threading.Thread(target=thread_stats)
th.start()