import  mysql.connector, requests, json, boto3, time
import pandas as pd
from botocore.exceptions import ClientError
from botocore.config import Config

instance_ids = ['i-04064013ac1862adf', 'i-0360438eeb0ed4afc', 'i-0cc80fcbd4dc96d6c', "i-012533eda9b15248f", "i-04b2f2abb77a085a8", "i-00f92c02d4a89d8bf", "i-04d218436060eaa68", "i-05a8c558bbab9cfdb"]


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
backend_app = 'http://localhost:5002'

def connect_to_database():
    return mysql.connector.connect(user=db_config['user'],
                                   password=db_config['password'],
                                   host=db_config['host'],
                                   port=db_config['port'],
                                   database=db_config['database'])          

def get_stats_logs():
    start_time = round((time.time() - 60) * 1000)
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
        
        return miss_rate
    return None

def get_pool_ready_count():
    global instance_ids

    active_count = 0
    unstable_count = 0
    try:
        ec2.describe_instances(InstanceIds=instance_ids, DryRun=True)
        print('Instance Status')
    except ClientError as e:
        if 'DryRunOperation' not in str(e):
            raise

    try:
        for instance in instance_ids:
            response = ec2.describe_instances(InstanceIds=[instance], DryRun=False)
            inst_name = response['Reservations'][0]['Instances'][0]['State']['Name']
            if (inst_name == 'pending' or inst_name == 'shutting-down' or inst_name == 'stopping'):
                unstable_count += 1
            elif (inst_name == 'running'):
                active_count += 1
        return unstable_count, active_count
    except ClientError as e:
        print(e)
	
def get_cache_policy():
    cnx = db
    cursor = cnx.cursor(buffered = True)
    query = '''SELECT * FROM cache_policy WHERE param_key = (SELECT MAX(param_key) FROM cache_policy LIMIT 1)'''
    cursor.execute(query)
    if(cursor._rowcount):# if key exists in db
        cache_policy=cursor.fetchone()
        return cache_policy
    return None

def auto_scale():
    global db, backend_app

    while (True):
        resp = requests.get(backend_app + "/getCachePoolConfig")
        pool_params = json.loads(resp.content.decode('utf-8'))
        print(pool_params)
        if pool_params['mode'] == 'automatic':
            # runs every minute
            unstable_count, active_count = get_pool_ready_count()
            # Unstable implies instances are stil starting, stopping or pending
            print("Active Count " + str(active_count))
            print("Unstable Count " + str(unstable_count))

            if unstable_count == 0:
                miss_rate = get_stats_logs()
                print("Current Miss Rate: " + str(miss_rate))
                # Miss rate is none, when no logs have been printed for this time period
                if not miss_rate == None:
                    cache_policy = get_cache_policy()
                    print(cache_policy)
                    if not cache_policy == None:
                        if miss_rate > cache_policy[1]:
                            # Max Miss Rate, Scale up instances
                            print("Scale up")
                            expand_factor = cache_policy[3]
                            max_startup = round(expand_factor * active_count)
                            if max_startup + active_count > 8:
                                # Start a max of 8 nodes
                                max_startup = 8 - active_count
                            
                            for i in range(max_startup):
                                print("Call startup node")
                                requests.post(backend_app + '/startInstance')

                        # Get current memcache count, then scale up max 8
                        elif miss_rate < cache_policy[2]:
                            # Min Miss Rate, Scale up instances
                            print("Scale Down")
                            shrink_factor = cache_policy[4]
                            max_shutdown = round(shrink_factor * active_count)
                            if  active_count - max_shutdown < 1:
                                # Shutdown max of all but 1
                                max_shutdown = active_count - 1
                            
                            for i in range(max_shutdown):
                                print("Call shutdown node")
                                requests.post(backend_app + '/stopInstance')
        time.sleep(60)
        




db = connect_to_database()
auto_scale()