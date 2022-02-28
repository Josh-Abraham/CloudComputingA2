from flask import Flask
import os

global UPLOAD_FOLDER

webapp = Flask(__name__)
UPLOAD_FOLDER = os.path.dirname(os.path.abspath(__file__)) + '/static/images'

from app import routes


