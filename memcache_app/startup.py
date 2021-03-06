import requests, os
import boto3
from botocore.exceptions import ClientError

instance_id_main = "i-043dc18a3aff50fe6" # Main host
access_key = os.getenv("AWS_ACCESS_KEY")
secret_key = os.getenv("AWS_SECRET_KEY")

ec2 = boto3.client('ec2', region_name='us-east-1', aws_access_key_id=access_key,
         aws_secret_access_key=secret_key)

def call_ready_request():
    try:
        ec2.describe_instances(InstanceIds=[instance_id_main], DryRun=True)
    except ClientError as e:
        if 'DryRunOperation' not in str(e):
            raise

    try:
        response = ec2.describe_instances(InstanceIds=[instance_id_main], DryRun=False)

        resp = requests.get("http://169.254.169.254/latest/meta-data/public-ipv4")
        instance_ip_address = resp.content.decode("utf-8")

        resp = requests.get("http://169.254.169.254/latest/meta-data/instance-id")
        instance_id = resp.content.decode("utf-8")

        print(instance_ip_address)
        print(instance_id)

        host_ip_address = response['Reservations'][0]['Instances'][0]['PublicIpAddress']
        address = 'http://' + str(host_ip_address) + ':5002/readyRequest'
        jsonReq = {
            "ip_address": instance_ip_address,
            "instance_id": instance_id
        }
        res = requests.post(address, json=jsonReq)
        print("Cache Parameter Response")
        print(res.content.decode("utf-8"))
        return res.content.decode("utf-8")
    except ClientError as e:
        print(e)
