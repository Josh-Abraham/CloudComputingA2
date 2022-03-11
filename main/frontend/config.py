import os

db_config = {'user': 'root',
             'password': 'ece1779pass',
             'host': '127.0.0.1',
             'database': 'ImageStore'}

max_capacity = 2
replacement_policy = 'Least Recently Used'

UPLOAD_FOLDER = os.path.dirname(os.path.abspath(__file__)) + '/static/images'