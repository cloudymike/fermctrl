#!/bin/bash

source variables.sh


# Enable google API
BILLINGACCOUNT=$(gcloud beta billing accounts list | tail -1 | cut -f 1 -d " ")
gcloud beta billing projects link $PROJECT_ID  --billing-account $BILLINGACCOUNT
gcloud services enable cloudbuild.googleapis.com --project $PROJECT_ID

# Create APP
gcloud app create --region=$REGION --project=$PROJECT_ID
