#!/bin/bash

source ../gcloudconfig/variables.sh

cd hello_world
python3 -m venv env
source env/bin/activate
pip install  -r requirements.txt

# Load app
gcloud app deploy --project $PROJECT_ID
gcloud app versions list --project $PROJECT_ID

gcloud app browse --project $PROJECT_ID
