from flask import render_template, request, send_file, redirect, url_for, g, jsonify
from flask import Blueprint
from frontend.image_utils.db_connection import get_db
from frontend.image_utils.image_utils import save_image, write_image_base64,save_image_automated
import requests, time, datetime
import frontend.image_utils.config as conf
import json

routes = Blueprint("routes", __name__)

# Memcache host port
cache_host = "http://localhost:5001"

cache_config = {
    'host_count': 1,
    'cache_size': '2',
    'replacement_policy': 'Least Recently Used'
}


@routes.errorhandler(404)
def not_found(e):
    """ Error template goes back to home
    """
    return render_template("home.html")

@routes.route('/')
@routes.route('/home')
def home():
    """ Main route, as well as default location for 404s
    """
    return render_template("home.html")

@routes.route('/add_key', methods = ['GET','POST'])
def add_key():
    """Add an image
    GET: Simply render the add_key page
    POST: Pass in key from form to add to DB and file system
    """
    if request.method == 'POST':
        key = request.form.get('key')
        status = save_image(request, key)
        return render_template("add_key.html", save_status=status)
    return render_template("add_key.html")

@routes.route('/show_image', methods = ['GET','POST'])
def show_image():
    """ Endpoint to show the image
    GET: Simply render the show_image page
    POST: Post request will check memcache first
    If it exists in cache, fetch it
    If doesn't exist, fetch file location from DB, and add to cache
    Display image as Base64
    """
    global cache_host
    if request.method == 'POST':
        key = request.form.get('key')
        jsonReq={"keyReq":key}
        res= requests.post(cache_host + '/get', json=jsonReq)
        if(res.text=='Unknown key'):#res.text is the file path of the image from the memcache
            #get from db and update memcache
            cnx = get_db()
            cursor = cnx.cursor(buffered=True)
            query = "SELECT image_tag FROM image_table where image_key= %s"
            cursor.execute(query, (key,))
            if(cursor._rowcount):# if key exists in db
                image_tag=str(cursor.fetchone()[0]) #cursor[0] is the imagetag recieved from the db
                #close the db connection
                cnx.close()
                #put into memcache
                filename=image_tag
                base64_image = write_image_base64(filename)
                jsonReq = {key:base64_image}
                res = requests.post(cache_host + '/put', json=jsonReq)
                return render_template('show_image.html', exists=True, filename=base64_image)
            else:#the key is not found in the db
                return render_template('show_image.html', exists=False, filename="does not exist")

        else:# the key was found in memcache
            # print("memcache response is:", res.text)
            return render_template('show_image.html', exists=True, filename=res.text)
    return render_template('show_image.html')


@routes.route("/get_image/<filename>")
def get_image(filename):
    """ This endpoint just returns the image
    The key is the filename with extension
    """
    filepath = "static/images/" + filename
    return send_file(filepath)

@routes.route('/key_store')
def key_store():
    """ Get list of all keys currently in the database
    """
    cnx = get_db()
    cursor = cnx.cursor()
    query = "SELECT image_key FROM image_table"
    cursor.execute(query)
    keys = []
    #make list of all keys in Database
    for key in cursor:
        keys.append(key[0])
    total=len(keys)

    #close db connection
    cnx.close()

    if keys:
        return render_template('key_store.html', keys=keys, total=total)
    else:
        return render_template('key_store.html')

# @webapp.route('/cache_stats')
# def cache_stats():
#     """ Endpoint to show the cache statistics
#     Generates and displays the 5 graphs/plots pertaining to the statistics
#     of the memcache for the past 10 minutes.
#     Display image as Base64
#     """
#     cnx = get_db()
#     cursor = cnx.cursor(dictionary=True)
#     stop_time = datetime.datetime.now()
#     start_time = stop_time - datetime.timedelta(minutes=10)
#     query = '''SELECT * FROM cache_stats cs WHERE cs.created_at > %s and cs.created_at < %s'''
#     cursor.execute(query, (start_time, stop_time))
#     rows = cursor.fetchall()
#     cnx.close()
    
#     (x_data, y_data) = prepare_data(rows)
#     image_map = {}
#     for k,v in y_data.items():
#         image_map[k] = plot_graphs(x_data['x-axis'], v, k)

#     return render_template('cache_stats.html', cache_count_plot = image_map['cache_count'], 
#                             request_plot = image_map['request_count'], cache_size_plot = image_map['cache_size'], 
#                              hit_plot = image_map['hit'], miss_plot = image_map['miss'])


# Test functionality
@routes.route('/api/list_keys', methods = ['POST'])
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

@routes.route('/api/key/<string:key_value>', methods = ['POST'])
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


@routes.route('/api/upload', methods = ['POST'])
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


