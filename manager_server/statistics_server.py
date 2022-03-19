# The file that will write to logging every 5 seconds
import requests
import boto3, time, datetime, json
from frontend.config import aws_config
from manager_server import memcache_pool
client = boto3.client('logs', region_name="us-east-1", aws_access_key_id=aws_config['aws_access_key_id'], aws_secret_access_key=aws_config['aws_secret_access_key'])
STATES = ['Starting', 'Stopping']

def thread_stats():
    while True:
        statistics = get_aggregate_statistics()
        message = json.dumps(statistics)
        create_log(message)
        time.sleep(5)

def create_log(message):
    sequence_token = None
    log_stream_resp = client.describe_log_streams(logGroupName="MetricLogs", logStreamNamePrefix="ApplicationLogs")
    if 'uploadSequenceToken' in log_stream_resp['logStreams'][0]:
        # Get previous Sequence Token if it exists
        sequence_token = log_stream_resp['logStreams'][0]['uploadSequenceToken']

    log_event = {
            'logGroupName': 'MetricLogs',
            'logStreamName': 'ApplicationLogs',
            'logEvents': [
                {
                    'timestamp': int(round(time.time() * 1000)),
                    'message': message
                },
            ],
        }
    if sequence_token:
        log_event['sequenceToken'] = sequence_token

    try:
        client.put_log_events(**log_event)
        print("Log created")
    except:
        print("Log not added")


def get_aggregate_statistics():
    global memcache_pool
    size, access_count, miss_rate, hit_rate, key_count, active_count = 0, 0, 0, 0, 0, 0
    for host in memcache_pool:
            address_ip = memcache_pool[host]
            if not address_ip == None and not address_ip in STATES: 
                try:
                    address = 'http://' + str(address_ip) + ':5000/getStatistics'
                    resp = requests.get(address)
                    resp_dict = json.loads(resp.content.decode("utf-8"))
                    size += resp_dict['size']
                    access_count += resp_dict['access_count']
                    miss_rate += resp_dict['miss_rate']
                    hit_rate += resp_dict['hit_rate']
                    key_count += resp_dict['key_count']
                    active_count += 1
                except:
                    print("")
    if active_count > 0:
        statistics = {
            'size': size/active_count, 
            'key_count': key_count/active_count,
            'access_count': access_count/active_count,
            'miss_rate': miss_rate/active_count,
            'active_count': active_count,
            'hit_rate': hit_rate/active_count
        }
        
        return statistics
    
    statistics = {
            'size': 0, 
            'access_count': 0,
            'key_count': 0,
            'miss_rate': 0,
            'hit_rate': 0,
            'active_count': 0
        }
    return statistics