#!/bin/bash

#Creating new project id's is a bad things as it takes 30 days to remove them
#PROJECTID=$(python -c "from coolname import generate_slug; x=generate_slug(2); print(x)")
PROJECTID=mhhelloworld-1
# This has to be done once on each computer to setup tools:
# sudo apt-get install -y google-cloud-sdk-app-engine-python
# sudo apt-get install -y python3-venv

# To avoid using PROJECTID option everywhere
# gcloud config set project $PROJECTID

# These will fail if you are reusing a project
# Skip or ignore errors
gcloud projects create  $PROJECTID --name="Hello World"
gcloud app create --region='us-central' --project=$PROJECTID

# Enable google API
BILLINGACCOUNT=$(gcloud beta billing accounts list | tail -1 | cut -f 1 -d " ")
gcloud beta billing projects link $PROJECTID  --billing-account $BILLINGACCOUNT
gcloud services enable cloudbuild.googleapis.com --project $PROJECTID
# End of skip

cd hello_world
python3 -m venv env
source env/bin/activate
pip install  -r requirements.txt

# Run app locally
# http://localhost:8080
#python main.py

gcloud app deploy --project $PROJECTID
gcloud app browse --project $PROJECTID

#read -p "Press enter to finish"
# Do NOT remove project as it takes 30 days for projects to be really removed
#gcloud projects delete $PROJECTID
