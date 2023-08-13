#!/bin/bash

# setup service account credentials
# see https://cloud.google.com/pubsub/docs/building-pubsub-messaging-system#create_service_account_credentials
#export GOOGLE_APPLICATION_CREDENTIALS=~/secrets/gcloud/myproject.json

# Load app
cd mqttrw
python3 -m venv venv
source venv/bin/activate
pip install  -r requirements.txt
pip freeze

cp ../../config/config.py .
python main.py
