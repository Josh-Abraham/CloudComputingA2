from flask import Flask
webapp = Flask(__name__)
memcache_pool = {
    "i-04064013ac1862adf": None,
    "i-0360438eeb0ed4afc": None
}
from manager_server import backend_client
