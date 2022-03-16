import os, requests, json
resp = requests.get("http://169.254.169.254/latest/user-data/")
conf_dict = json.loads(resp.content.decode('utf-8'))

db_config = {'user': conf_dict["MYSQL_USER"],
             'password': conf_dict["MYSQL_PASSWORD"],
             'host': conf_dict["MYSQL_HOST"],
             'port': '3306',
             'database': 'ImageStore'}

aws_config = {
    'aws_access_key_id': conf_dict['aws_access_key_id'],
    'aws_secret_access_key': conf_dict['aws_secret_access_key']
}

max_capacity = 2
replacement_policy = 'Least Recently Used'

UPLOAD_FOLDER = os.path.dirname(os.path.abspath(__file__)) + 'main/frontend/static/images'