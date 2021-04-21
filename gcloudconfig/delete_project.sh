#!/bin/bash

source variables.sh

echo Do not delete, exiting
exit 1
# Do NOT remove project as it takes 30 days for projects to be really removed
gcloud projects delete $PROJECT_ID
