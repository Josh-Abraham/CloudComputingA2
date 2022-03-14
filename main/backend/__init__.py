from flask import Flask
webapp = Flask(__name__)
memcache_pool = {
    "i-04064013ac1862adf": None
}
from backend import backend_client
