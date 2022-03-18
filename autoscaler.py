import  mysql.connector, requests, json, boto3, time
import pandas as pd
from botocore.exceptions import ClientError
from botocore.config import Config
resp = requests.get("http://169.254.169.254/latest/user-data/")
conf_dict = json.loads(resp.content.decode('utf-8'))

my_config = Config(
    region_name = 'us-east-1',
    #signature_version = 'v4',
    retries = {
        'max_attempts': 10,
        'mode': 'standard'
    }
)

db_config = {'user': conf_dict["MYSQL_USER"],
             'password': conf_dict["MYSQL_PASSWORD"],
             'host': conf_dict["MYSQL_HOST"],
             'port': '3306',
             'database': 'ImageStore'}

aws_config = {
    'aws_access_key_id': conf_dict['aws_access_key_id'],
    'aws_secret_access_key': conf_dict['aws_secret_access_key']
}

log_client = boto3.client('logs', region_name="us-east-1", aws_access_key_id=aws_config['aws_access_key_id'], aws_secret_access_key=aws_config['aws_secret_access_key'])
ec2 = boto3.client('ec2', config=my_config,aws_access_key_id= aws_config['aws_access_key_id'], aws_secret_access_key= aws_config['aws_secret_access_key'])



def connect_to_database():
    return mysql.connector.connect(user=db_config['user'],
                                   password=db_config['password'],
                                   host=db_config['host'],
                                   port=db_config['port'],
                                   database=db_config['database'])
                        

def get_stats_logs():
    start_time = round((time.time() - 30*60) * 1000)
    current_time = round(time.time() * 1000)

    response = log_client.get_log_events(
        logGroupName='MetricLogs',
        logStreamName='ApplicationLogs',
        startTime=int(start_time),
        endTime=int(current_time),
        startFromHead=True
    )

    log_events = response['events']

    data = []
    for each_event in log_events:
        timestamp = each_event['timestamp']
        data_obj = json.loads(each_event['message'])
        data_obj['timestamp'] = timestamp * 1000000
        data.append(data_obj)

    data = pd.DataFrame(data)
    if not data.empty:
        data['timestamp']= pd.to_datetime(data['timestamp'])
        sample_data = data.resample('2Min', on='timestamp').mean()
        miss_rate = sample_data.iloc[-1]['miss_rate']
        hit_rate = sample_data.iloc[-1]['hit_rate']
        return (miss_rate, hit_rate)
    return None

def get_pool_ready(instance_ids):
    try:
        ec2.describe_instances(InstanceIds=instance_ids, DryRun=True)
        print('Instance Status')
    except ClientError as e:
        if 'DryRunOperation' not in str(e):
            raise

    try:
        response = ec2.describe_instances(InstanceIds=instance_ids, DryRun=False)
        for instance in response['Reservations'][0]['Instances']:
            print(instance['InstanceId'])
            if (instance['State']['Name'] == 'pending' or instance['State']['Name'] == 'shutting-down' or instance['State']['Name'] == 'stopping'):
                return False
        return True
    except ClientError as e:
        print(e)
	

def auto_scale(cache_policy):
    # runs every 1 minute
    
    data = get_stats_logs()
    if not data == None:
        miss_rate = data[0]
        hit_rate = data[1]
        if miss_rate > cache_policy['max_miss_rate']:
            # Scale up instances
            print("Scale up")
            # Get current memcache count, then scale up max 8
        elif miss_rate < cache_policy['min_miss_rate']:
            print("Scale Down")

        print(miss_rate)

cache_policy = {
    'max_miss_rate': 0,
    'min_miss_rate': 0, 
    'exp_ratio': 0,
    'shrink_ratio': 0
}

auto_scale(cache_policy)