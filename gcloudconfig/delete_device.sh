#!/bin/bash

source variables.sh

# Create subscription
gcloud pubsub subscriptions delete $TOPIC --project=$PROJECT_ID
gcloud pubsub topics delete $TOPIC --project=$PROJECT_ID

gcloud iot devices delete $DEVICE_ID \
  --project=$PROJECT_ID \
  --registry=$REGISTRY_ID \
  --region=$REGION


gcloud iot registries delete $REGISTRY_ID \
  --project=$PROJECT_ID \
  --region=$REGION

rm -f *.pem
