#################
#  ECE 1779 A2  #
#################

gunicorn --bind 0.0.0.0:5000 wsgi_frontend:webapp &
gunicorn --bind 0.0.0.0:5001 wsgi_manager:webapp &
gunicorn --bind 0.0.0.0:5002 wsgi_server:webapp &
python3 autoscaler.py
echo "Webapps started"