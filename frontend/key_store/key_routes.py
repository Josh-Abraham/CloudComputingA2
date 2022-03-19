from flask import Blueprint, jsonify, render_template, request, send_file, redirect
from frontend.db_connection import get_db
from frontend.key_store.image_utils import *
import requests, json

image_routes = Blueprint("image_routes", __name__)

# Memcache host port
backend_app = "http://localhost:5002"


@image_routes.route('/add_key', methods = ['GET','POST'])
def add_key():
    """Add an image
    GET: Simply render the add_key page
    POST: Pass in key from form to add to DB and file system
    """
    if request.method == 'POST':
        key = request.form.get('key')
        status = upload_image(request, key)
        return render_template("add_key.html", save_status=status)
    return render_template("add_key.html")

@image_routes.route('/show_image', methods = ['GET','POST'])
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
        # TODO: Add Memcache get
        ip_resp = requests.get(backend_app + '/hash_key', json=jsonReq)
        ip_dict = json.loads(ip_resp.content.decode('utf-8'))
        ip=ip_dict[1]
        res= requests.post('http://'+ str(ip) + ':5000/get', json=jsonReq)
        #res = None
        if(res == None or res.text=='Unknown key'):
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
                image=download_image(image_tag)
                jsonReq = {key:image}
                # TODO: Add to Cache
                res = requests.post('http://'+ str(ip) + ':5000/put', json=jsonReq)
                return render_template('show_image.html', exists=True, filename=image)
            else:#the key is not found in the db
                return render_template('show_image.html', exists=False, filename="does not exist")

        else:
            return render_template('show_image.html', exists=True, filename=res.text)
    return render_template('show_image.html')


@image_routes.route("/get_image/<filename>")
def get_image(filename):
    """ This endpoint just returns the image
    The key is the filename with extension
    """
    filepath = "static/images/" + filename
    return send_file(filepath)

@image_routes.route('/key_store')
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


@image_routes.route('/navigate')
def navigate():
	hostname = request.headers.get('Host').split(':')[0]
	print(hostname)
	return redirect('http://'+hostname + ':5001')
