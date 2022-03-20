from frontend.config import aws_config, UPLOAD_FOLDER
import os, requests, base64
from frontend.db_connection import get_db
from frontend.key_store import s3_storage
import tempfile, json
import boto3
from botocore.config import Config
ALLOWED_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.gif'}

my_config = Config(
    region_name = 'us-east-1',
    #signature_version = 'v4',
    retries = {
        'max_attempts': 10,
        'mode': 'standard'
    }
)

s3 =boto3.client('s3',config=my_config,aws_access_key_id= aws_config['aws_access_key_id'], aws_secret_access_key= aws_config['aws_secret_access_key'])

backend_app = "http://localhost:5002"

def upload_image(request,key):
    global backend_app
    img_url = request.form.get('img_url')
    if img_url == "":
        file = request.files['file']
        _, extension = os.path.splitext(file.filename)
        if extension.lower() in ALLOWED_EXTENSIONS:
            try:
                print("trying")
                base64_image = base64.b64encode(file.read())
                s3.put_object(Body=base64_image,Key=key,Bucket="image-bucket-a2",ContentType='image')
                print("uploaded")
                #TODO: memcache invalidate
                jsonReq={"keyReq":key}
                ip_resp = requests.get(backend_app + '/hash_key', json=jsonReq)
                ip_dict = json.loads(ip_resp.content.decode('utf-8'))
                ip=ip_dict[1]
                res = requests.post('http://'+ str(ip) +':5000/invalidate', json=jsonReq)
                return write_img_db(key, key)
            except:
                return "INVALID"
            # return "SAVED"
        return "INVALID"

    response = requests.get(img_url)
    if response.status_code == 200:
        _, extension = os.path.splitext(img_url)
        if extension.lower() in ALLOWED_EXTENSIONS:
            filename = key + extension
            with open(filename, 'wb') as f:
               f.write(response.content)
               f.seek(0)
            with open(filename, 'rb') as f:
               base64_image = base64.b64encode(f.read())
            f.close()
            os.remove(filename)
            s3.put_object(Body=base64_image,Key=key,Bucket="image-bucket-a2",ContentType='image')
            #TODO: memcache invalidate
            try:
                jsonReq={"keyReq":key}
                ip_resp = requests.get(backend_app + '/hash_key', json=jsonReq)
                ip_dict = json.loads(ip_resp.content.decode('utf-8'))
                ip=ip_dict[1]
                res = requests.post('http://'+ str(ip) +':5000/invalidate', json=jsonReq)
                return write_img_db(key, key)
            except:
                return "INVALID"
    return "INVALID"

def download_image(key):
    with open('Temp.txt', 'wb') as file:
        s3.download_fileobj('image-bucket-a2', key, file)
    with open('Temp.txt', 'rb') as file:
        base64_image = file.read().decode('utf-8')
    file.close()
    os.remove("Temp.txt")
    print("downloaded")
    return base64_image


def write_image_base64(filename):
    """ Write image out in base64
    """
    with open(UPLOAD_FOLDER + "/" + filename, "rb") as img_file:
        base64_image = base64.b64encode(img_file.read())
    base64_image = base64_image.decode('utf-8')
    return base64_image

def write_img_db(image_key, image_tag):
    """ Write image to DB

        Parameters:
            image_key (int): key value
            image_tag (str): file name

        Return:
            response (str): "OK" or "ERROR"
    """
    if image_key == "" or image_tag == "":
        error_msg="FAILURE"
        return error_msg
    try:
        cnx = get_db()
        cursor = cnx.cursor(buffered = True)
        query_exists = "SELECT EXISTS(SELECT 1 FROM image_table WHERE image_key = (%s))"
        cursor.execute(query_exists,(image_key,))
        for elem in cursor:
            if elem[0] == 1:
                query_remove = '''DELETE FROM image_table WHERE image_key=%s'''
                cursor.execute(query_remove,(image_key,))
                break

        query_add = ''' INSERT INTO image_table (image_key,image_tag) VALUES (%s,%s)'''
        cursor.execute(query_add,(image_key,image_tag))
        cnx.commit()
        cnx.close()
        return "OK"
    except:
        return "FAILURE"

# TODO: Do we need to update this?
def save_image_automated(request, key):
    """ check if the file in request is an image and save into local storage,
        calls write_to_db, and invalidates
        memcache for the key if it is in the memcache-
        function used only for automatic endpoint

        Parameters:
            request (request module): holds the form data for the image save
            key (str): key to reference the file

        Return:
            response (str): "OK" or "ERROR"
    """
    try:
        file = request.files['file']
        _, extension = os.path.splitext(file.filename)
        if extension.lower() in ALLOWED_EXTENSIONS:
            try:
                print("trying")
                base64_image = base64.b64encode(file.read())
                s3.put_object(Body=base64_image,Key=key,Bucket="image-bucket-a2",ContentType='image')
                print("uploaded")
                #TODO: memcache invalidate
                jsonReq={"keyReq":key}
                ip_resp = requests.get(backend_app + '/hash_key', json=jsonReq)
                ip_dict = json.loads(ip_resp.content.decode('utf-8'))
                ip=ip_dict[1]
                res = requests.post('http://'+ str(ip) +':5000/invalidate', json=jsonReq)
                return write_img_db(key, key)
            except:
                return "INVALID"
        return "INVALID"
    except:
        return "INVALID"
