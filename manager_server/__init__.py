from flask import Flask
import threading
webapp = Flask(__name__)
memcache_pool = {
    "i-04064013ac1862adf": None,
    "i-0360438eeb0ed4afc": None,
    "i-0cc80fcbd4dc96d6c": None,
    "i-012533eda9b15248f": None,
    "i-04b2f2abb77a085a8": None,
    "i-00f92c02d4a89d8bf": None,
    "i-04d218436060eaa68": None,
    "i-05a8c558bbab9cfdb": None
}
from manager_server import backend_client
from manager_server.statistics_server import thread_stats

th = threading.Thread(target=thread_stats)
th.start()