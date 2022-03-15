from flask import Blueprint, jsonify, request
from frontend.db_connection import get_db
from frontend.key_store.image_utils import *
import requests

api_routes = Blueprint("api_routes", __name__)

# Memcache host port
cache_host = "http://localhost:5001"

# Test functionality
@api_routes.route('/api/list_keys', methods = ['POST'])
def list_keys():
    """
    Automatic test endpoint to list all keys currently in the database

    Return: in case of success json with success status and list of keys
            in case of failure json with success status and the error
    """
    try:
        cnx = get_db()
        cursor = cnx.cursor()
        query = "SELECT image_key FROM image_table"
        cursor.execute(query)
        keys = []
        #make list of all keys in Database
        for key in cursor:
            keys.append(key[0])
        cnx.close()
        data_out={"success":"true" , "keys":keys}
        return jsonify(data_out)

    except Exception as e:
        error_message={"success":"false" , "error":{"code":"500 Internal Server Error", "message":"Something Went Wrong"}}
        return(jsonify(error_message))

@api_routes.route('/api/key/<string:key_value>', methods = ['POST'])
def one_key(key_value):
    """
    Automatic test endpoint to retrieve the image associated with the given key
    Post request will check memcache first
    If it exists in cache, fetch it
    If doesn't exist, fetch file location from DB, and add to cache
    convert image file to Base64

    Return: in case of success json with success status and contents of the image in Base64 format
            in case of failure json with success status and the error
    """
    try:
        jsonReq={"keyReq":key_value}
        res= requests.post('http://localhost:5001/get', json=jsonReq)
        if(res.text=='Unknown key'):#res.text is the file path of the image from the memcache
            #get from db and update memcache
            cnx = get_db()
            cursor = cnx.cursor(buffered=True)
            query = "SELECT image_tag FROM image_table where image_key= %s"
            cursor.execute(query, (key_value,))
            if(cursor._rowcount):# if key exists in db
                image_tag=str(cursor.fetchone()[0]) #cursor[0] is the imagetag recieved from the db
                #close the db connection
                cnx.close()
                #put into memcache
                filename=image_tag
                base64_image = write_image_base64(filename)
                jsonReq = {key_value:base64_image}
                res = requests.post(cache_host + '/put', json=jsonReq)
                data_out={"success":"true" , "content":base64_image}
                #output json with db values
                return jsonify(data_out)

            else:#the key is not found in the db
                data_out={"success":"false" , "error":{"code": "406 Not Acceptable", "message":"specified key does not not exist"}}
                return jsonify(data_out)

        else:
            data_out={"success":"true" , "content":res.text}
            return jsonify(data_out)

    except Exception as e:
        error_message={"success":"false" , "error":{"code":"500 Internal Server Error", "message":"Something Went Wrong"}}
        return(jsonify(error_message))


@api_routes.route('/api/upload', methods = ['POST'])
def upload():
    """
    Automatic test endpoint to upload the given key image pair in the Database
    store the image in the local storage
    invalidate the key and image in the memcache

    Return: in case of success json with success status
            in case of failure json with success status and the error
    """
    try:
        key = request.form.get('key')
        status = save_image_automated(request, key)
        if status=="INVALID" or status== "FAILURE":
            data_out={"success":"false" , "error":{"code": "500 Internal Server Error", "message":"Failed to upload image"}}
            return jsonify(data_out)

        data_out={"success":"true"}
        return jsonify(data_out)

    except Exception as e:
        error_message={"success":"false" , "error":{"code":"500 Internal Server Error", "message":"Something Went Wrong"}}
        return(jsonify(error_message))


