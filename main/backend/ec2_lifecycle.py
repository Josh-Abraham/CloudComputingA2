import sys
import boto3
from botocore.exceptions import ClientError
from botocore.config import Config

my_config = Config(
    region_name = 'us-east-1',
    #signature_version = 'v4',
    retries = {
        'max_attempts': 10,
        'mode': 'standard'
    }
)

ec2 = boto3.client('ec2',config=my_config,aws_access_key_id= 'AKIA3U4U6D42HAMEVXES', aws_secret_access_key= '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')

def startup(instance_id):
    print('Starting instance ' + instance_id)
    try:
        ec2.start_instances(InstanceIds=[instance_id], DryRun=True)
    except ClientError as e:
        if 'DryRunOperation' not in str(e):
            raise

    # Dry run succeeded, run start_instances without dryrun
    try:
        response = ec2.start_instances(InstanceIds=[instance_id], DryRun=False)
        print(response)
    except ClientError as e:
        print(e)


def shutdown(instance_id):
    print('Shutting down instance ' + instance_id)
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
