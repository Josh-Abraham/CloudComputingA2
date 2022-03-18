import boto3, time, json
from datetime import datetime
from numpy import NaN
import pandas as pd
from frontend.config import aws_config
client = boto3.client('logs', region_name="us-east-1", aws_access_key_id=aws_config['aws_access_key_id'], aws_secret_access_key=aws_config['aws_secret_access_key'])


def get_stats_logs():
    

    HALF_HOUR = 30*60
    start_time = round((time.time() - HALF_HOUR) * 1000)
    current_time = round(time.time() * 1000)

    response = client.get_log_events(
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
    
    data['timestamp']= pd.to_datetime(data['timestamp'])
    sample_data = data.resample('1Min', on='timestamp').mean()

    miss_count = list(sample_data['miss_rate'].values)
    hit_count = list(sample_data['hit_rate'].values)
    miss_rate = []
    hit_rate = []
    for i in range(len(miss_count)):
        if (miss_count[i] + hit_count[i]) == 0:
            miss_rate.append(0)
            hit_rate.append(0)
        else:
            miss_r = (miss_count[i]/(miss_count[i] + hit_count[i])) * 100
            hit_r = (hit_count[i]/(miss_count[i] + hit_count[i])) * 100
            miss_rate.append(miss_r)
            hit_rate.append(hit_r)


    
    data_arr = [
        list(sample_data.index.values.astype(datetime)),
        list(sample_data['size'].values),
        miss_rate,
        hit_rate,
        list(sample_data['key_count'].values),
        list(sample_data['access_count'].values),
        list(sample_data['active_count'].values)
    ]

    return data_arr
