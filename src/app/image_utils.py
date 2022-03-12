from app import UPLOAD_FOLDER
import os, requests, base64
from app.db_connection import get_db
from main.backend import s3_storage
import tempfile
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

s3 =boto3.client('s3',config=my_config,aws_access_key_id= 'AKIA3U4U6D42HAMEVXES', aws_secret_access_key= '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')

def save_image(request, key):
    """ check if the file or url in request is an image and save into local storage,
        calls write_to_db, and invalidates
        memcache for the key if it is in the memcache

        Parameters:
            request (request module): holds the form data for the image save
            key (str): key to reference the file

        Return:
            response (str): "OK" or "ERROR"
    """
    img_url = request.form.get('img_url')
    if img_url == "":
        file = request.files['file']
        _, extension = os.path.splitext(file.filename)

        if extension.lower() in ALLOWED_EXTENSIONS:
            filename = key + extension
            file.save(os.path.join(UPLOAD_FOLDER, filename))
            jsonReq = {"key":key}
            res = requests.post('http://localhost:5001/invalidate', json=jsonReq)
            return write_img_db(key, filename)
        return "INVALID"
    try:
        response = requests.get(img_url)
        if response.status_code == 200:
            _, extension = os.path.splitext(img_url)
            filename = key + extension
            if extension.lower() in ALLOWED_EXTENSIONS:
                with open(UPLOAD_FOLDER + "/" + filename, 'wb') as f:
                    f.write(response.content)
                jsonReq = {"key":key}
                res = requests.post('http://localhost:5001/invalidate', json=jsonReq)
                return write_img_db(key, filename)
        return "INVALID"
    except:
        return "INVALID"

def upload_image(request,key):
    img_url = request.form.get('img_url')
    if img_url == "":
        file = request.files['file']
        _, extension = os.path.splitext(file.filename)
        if extension.lower() in ALLOWED_EXTENSIONS:
            print("trying")
            base64_image = base64.b64encode(file.read())
            s3.put_object(Body=base64_image,Key=key,Bucket="image-bucket-a2",ContentType='image')
            print("u0loaded")
            jsonReq = {"key":key}
            res = requests.post('http://localhost:5001/invalidate', json=jsonReq)
            return "SAVED"
        return "INVALID"

    response = requests.get(img_url)
    if response.status_code == 200:
        _, extension = os.path.splitext(img_url)
        if extension.lower() in ALLOWED_EXTENSIONS:
            filename = key + extension
            with open(UPLOAD_FOLDER + "/" + filename, 'r+b') as f:
               f.write(response.content)
               f.seek(0)
               base64_image = base64.b64encode(f.read())
            f.close()
            print(response.content)
            print(base64_image)
            os.remove(UPLOAD_FOLDER + "/" + filename)
            s3.put_object(Body=base64_image,Key=key,Bucket="image-bucket-a2",ContentType='image')
            jsonReq = {"key":key}
            res = requests.post('http://localhost:5001/invalidate', json=jsonReq)
            return "SAVED"
    return "INVALID"

def download_image(key):
    with open('Temp.txt', 'wb') as file:
        s3.download_fileobj('image-bucket-a2', key, file)
    with open('Temp.txt', 'rb') as file:
        base64_image = file.read().decode('utf-8')
    file.close()
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
        extension=extension.lower()
        if extension.lower() in ALLOWED_EXTENSIONS:
            filename = key + extension
            file.save(os.path.join(UPLOAD_FOLDER, filename))
            jsonReq = {"key":key}
            res = requests.post('http://localhost:5001/invalidate', json=jsonReq)
            return write_img_db(key, filename)
        return "INVALID"

    except:
        return "INVALID"