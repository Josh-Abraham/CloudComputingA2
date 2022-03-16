import os

db_config = {'user': 'admin',
             'password': '',
             'host': 'a2-database.cjfk7vbroptm.us-east-1.rds.amazonaws.com',
             'port': '3306',
             'database': 'ImageStore'}
#
max_capacity = 2
replacement_policy = 'Least Recently Used'

UPLOAD_FOLDER = os.path.dirname(os.path.abspath(__file__)) + 'main/frontend/static/images'
