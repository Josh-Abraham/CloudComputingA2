import boto3
from botocore.exceptions import ClientError
from botocore.config import Config
import logging
import os,base64
from frontend.config import aws_config

my_config = Config(
    region_name = 'us-east-1',
    #signature_version = 'v4',
    retries = {
        'max_attempts': 10,
        'mode': 'standard'
    }
)

def upload_file(file_name, bucket, s3=None,object_name=None ):
    """Upload a file to an S3 bucket

    :param file_name: File to upload
    :param bucket: Bucket to upload to
    :param object_name: S3 object name. If not specified then file_name is used
    :return: True if file was uploaded, else False
    """

    # If S3 object_name was not specified, use file_name
    if object_name is None:
        object_name = os.path.basename(file_name)
        print("object created")

    # Upload the file
    if s3 is None:
        s3 = boto3.client('s3',config=my_config,aws_access_key_id= aws_config['aws_access_key_id'], aws_secret_access_key= aws_config['aws_secret_access_key'])
        print("client created")
    try:
        print("trying")
        response = s3.upload_file(Filename=file_name, Bucket=bucket, Key=object_name)
        print("uploaded")
    except ClientError as e:
        logging.error(e)
        return False
    return True

'''def download_file(key,bucket='image-bucket-a2',s3=None):
    if s3 is None:
        s3 = boto3.client('s3',config=my_config,aws_access_key_id= aws_config['aws_access_key_id'], aws_secret_access_key= aws_config['aws_secret_access_key'])
        print("client created")

    try:
        print("trying")
        with open('Temp.txt', 'r+b') as f:
            s3.download_fileobj(Bucket=bucket, Key=key,f )
            base64_image = f.read().decode('utf-8')
        print("downloaded")
        return base64_image
    except ClientError as e:
        logging.error(e)
        return False
    return True'''




#s3 =boto3.client('s3',config=my_config,aws_access_key_id= aws_config['aws_access_key_id'], aws_secret_access_key= aws_config['aws_secret_access_key'])
'''s3.download_file()
print('Existing buckets:')
for bucket in response['Buckets']:
    print(f'  {bucket["Name"]}')'''
