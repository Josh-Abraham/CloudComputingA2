import boto3, time, datetime, json

client = boto3.client('logs', region_name="us-east-1", aws_access_key_id='AKIA3U4U6D42HAMEVXES', aws_secret_access_key='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')

retention_period_in_days = 1

# Back end Log Group

log_group = 'MetricLogs'
message = '{"Miss Rate": 100, "Hit Rate": 50}'

sequence_token = None
log_stream_resp = client.describe_log_streams(logGroupName="MetricLogs", logStreamNamePrefix="ApplicationLogs")
if 'uploadSequenceToken' in log_stream_resp['logStreams'][0]:
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

response = client.put_log_events(**log_event)
print("Created log")
time.sleep(5)

print("Log generated successfully")


response = client.get_log_events(
    logGroupName='MetricLogs',
    logStreamName='ApplicationLogs',
    startTime=int(datetime.datetime(2022, 3, 15, 0, 0).strftime('%s'))*1000,
    endTime=int(datetime.datetime(2022, 3, 18, 0, 0).strftime('%s'))*1000,
    startFromHead=True
)

log_events = response['events']

for each_event in log_events:
    print(each_event)
    print(json.loads(each_event['message']))
