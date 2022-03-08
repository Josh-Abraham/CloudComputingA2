import sys
import boto3
from botocore.exceptions import ClientError

instance_id = "i-04064013ac1862adf"
# action = sys.argv[1].upper()

ec2 = boto3.client('ec2')

try:
    ec2.stop_instances(InstanceIds=[instance_id], DryRun=True)
    print('Instance Stopped')
except ClientError as e:
    if 'DryRunOperation' not in str(e):
        raise

# Dry run succeeded, call stop_instances without dryrun
try:
    response = ec2.stop_instances(InstanceIds=[instance_id], DryRun=False)
    print(response)
except ClientError as e:
    print(e)
