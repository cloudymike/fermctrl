#!/bin/bash

source variables.sh

#Creating new project id's is a bad things as it takes 30 days to remove them
#PROJECTID=$(python -c "from coolname import generate_slug; x=generate_slug(2); print(x)")

# To avoid using PROJECTID option everywhere
# gcloud config set project $PROJECTID

# These will fail if you are reusing a project
# Skip or ignore errors
gcloud projects list --filter="project_id:$PROJECT_ID" | grep $PROJECT_ID
R1=$?
if [ "$R1" != "0" ]
then
gcloud projects create  $PROJECT_ID --name="$PROJECT_ID"
fi
