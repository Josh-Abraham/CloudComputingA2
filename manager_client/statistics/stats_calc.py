import boto3, time, datetime, json
import pandas as pd
from frontend.config import aws_config
client = boto3.client('logs', region_name="us-east-1", aws_access_key_id=aws_config['aws_access_key_id'], aws_secret_access_key=aws_config['aws_secret_access_key'])

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
    data.append(json.loads(each_event['message']))

data = pd.DataFrame(data)  
print(type(data.index[0]))

data['time']= pd.to_datetime(data['time'])



print(data.resample('1Min', on='time').mean())
