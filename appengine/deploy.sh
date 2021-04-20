#!/bin/bash

source ../gcloudconfig/variables.sh

cd app
python3 -m venv env
source env/bin/activate
pip install  -r requirements.txt
cp ../../gcloudconfig/config.py .
# Load app
gcloud app deploy --project $PROJECT_ID
gcloud app versions list --project $PROJECT_ID

gcloud app browse --project $PROJECT_ID
