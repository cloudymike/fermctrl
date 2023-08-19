#!/bin/bash

# Load app
cd web
python3 -m venv venv
source venv/bin/activate
pip install  -r requirements.txt
pip freeze

cp ../../config/config.py .

export FLASK_ENV=development
export FLASK_APP=main.py
export FLASK_RUN_PORT=8081
export FLASK_RUN_HOST="127.0.0.1"
flask run