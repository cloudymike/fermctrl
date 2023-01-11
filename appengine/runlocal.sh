#!/bin/bash

# setup service account credentials
# see https://cloud.google.com/pubsub/docs/building-pubsub-messaging-system#create_service_account_credentials
#export GOOGLE_APPLICATION_CREDENTIALS=~/secrets/gcloud/myproject.json

# Load app
cd app
python3 -m venv venv
source venv/bin/activate
pip install  -r requirements.txt
pip freeze

cp config_local.py config.py
# Run app locally
# http://localhost:8080
python mainlocal.py
