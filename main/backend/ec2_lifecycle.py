import sys, boto3, threading, time
from botocore.exceptions import ClientError
from backend import memcache_pool

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
        th = threading.Thread(target=threadInstanceCheck, args=(instance_id,))
        th.start()
        print(response)
    except ClientError as e:
        print(e)

def threadInstanceCheck(instance_id):
    global memcache_pool
    print('In Shutdown Thread')
    try:
        ec2.describe_instances(InstanceIds=[instance_id], DryRun=True)
        print('Instance Status')
    except ClientError as e:
        if 'DryRunOperation' not in str(e):
            raise

    # Dry run succeeded, call describe_instance_status without dryrun
    iterations = 0
    while(iterations < 15):
        try:
            response = ec2.describe_instances(InstanceIds=[instance_id], DryRun=False)
            iterations += 1
            resp_state = response['Reservations'][0]['Instances'][0]['State']['Name']
            print("Instance: " + instance_id + " state: " + resp_state)
            if resp_state == 'stopped':
                break
            time.sleep(4)
        except ClientError as e:
            print(e)
    memcache_pool[instance_id] = None

def set_pool_status():
    global memcache_pool
    print('Checking all Nodes')
    instances = list(memcache_pool.keys())
    try:
        ec2.describe_instances(InstanceIds=instances, DryRun=True)
        print('Instance Status')
    except ClientError as e:
        if 'DryRunOperation' not in str(e):
            raise

    # Dry run succeeded, call describe_instance_status without dryrun
    startCount = 0
    try:
        response = ec2.describe_instances(InstanceIds=instances, DryRun=False)
        for instance in response['Reservations'][0]['Instances']:
            print(instance['InstanceId'])
            if (instance['State']['Name'] == 'running'):
                memcache_pool[instance['InstanceId']] = instance['PublicIpAddress']
                startCount += 1
            else:
                memcache_pool[instance['InstanceId']] = None
        return startCount
    except ClientError as e:
        print(e)
    

