#!/bin/bash

# Load app
cd web
python3 -m venv venv
source venv/bin/activate
pip install  -r requirements.txt
pip freeze

cp ../../config/config.py .
# Run app locally
# http://localhost:8081
python main.py
