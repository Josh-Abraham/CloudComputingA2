from flask import Flask
import os

global UPLOAD_FOLDER

webapp = Flask(__name__)

from charts import routes


