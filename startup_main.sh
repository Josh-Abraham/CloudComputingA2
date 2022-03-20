#!/bin/sh
cd /home/ubuntu
pip install flask
pip install cachetools
pip install boto3
pip install botocore.exceptions
python3 run_backend.py
python3 run_frontend.py
python3 run_manager.py
python3 autoscaler.py
