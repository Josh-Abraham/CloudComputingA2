import sys, time, requests
import boto3
from botocore.exceptions import ClientError

instance_id = "i-04064013ac1862adf"
# action = sys.argv[1].upper()

ec2 = boto3.client('ec2')

try:
    ec2.start_instances(InstanceIds=[instance_id], DryRun=True)
except ClientError as e:
    if 'DryRunOperation' not in str(e):
        raise

# Dry run succeeded, run start_instances without dryrun
try:
    response = ec2.start_instances(InstanceIds=[instance_id], DryRun=False)
    print(response)
    time.sleep(3)
    runs = 0
    start_up = False
    while not start_up and runs < 20:
        time.sleep(3)
        try:
            response = ec2.describe_instance_status(InstanceIds=[instance_id], DryRun=False)
            print(response)
            runs += 1
            if len(response['InstanceStatuses']) > 0:
                status = response['InstanceStatuses'][0]['InstanceState']['Name']
                print(status)
                start_up = status == 'running'
            
        except ClientError as e:
            print(e)
            break

    if start_up:
        try:
            response = ec2.describe_instances(InstanceIds=[instance_id], DryRun=False)
            ip_address = response['Reservations'][0]['Instances'][0]['PublicIpAddress']
            print(ip_address)
            address = 'http://' + str(ip_address) + ':5000/ping'
            print(address)
            time.sleep(20)
            res = requests.get(address)
            print("HERE")
            
        except:
            print('Address Not Found')
except ClientError as e:
    print(e)

