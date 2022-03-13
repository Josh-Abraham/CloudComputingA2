import sys
import boto3
from botocore.exceptions import ClientError

ec2 = boto3.client('ec2')

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

def threadInstanceCheck(instance_id):
    #TODO: Working here on threaded check of status
    try:
        ec2.describe_instance_status(InstanceIds=[instance_id], DryRun=True)
        print('Instance Status')
    except ClientError as e:
        if 'DryRunOperation' not in str(e):
            raise

    # Dry run succeeded, call describe_instance_status without dryrun
    try:
        response = ec2.describe_instance_status(InstanceIds=[instance_id], DryRun=False)
        print(response)
    except ClientError as e:
        print(e)