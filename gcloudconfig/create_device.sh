#!/bin/bash

source variables.sh

# Generate your public / private keypair.
openssl genrsa -out rsa_private.pem 2048
openssl rsa -in rsa_private.pem -pubout -out rsa_public.pem

gcloud iot registries create $REGISTRY_ID \
    --project=$PROJECT_ID \
    --region=$REGION \
    --event-notification-config=topic=$TOPIC \
    --state-pubsub-topic=$STATE_PUBSUB_TOPIC

gcloud iot devices create $DEVICE_ID \
  --project=$PROJECT_ID \
  --region=$REGION \
  --registry=$REGISTRY_ID \
  --public-key path=rsa_public.pem,type=rsa-pem

# Create a python config file
cat << EOF > config.py
google_cloud_config = {
    'project_id':'$PROJECT_ID',
    'cloud_region':'$REGION',
    'registry_id':'$REGISTRY_ID',
    'device_id':'$DEVICE_ID',
    'mqtt_bridge_hostname':'mqtt.googleapis.com',
    'mqtt_bridge_port':8883
}

jwt_config = {
    'algorithm':'RS256',
    'token_ttl': 43200, #12 hours
    # Use utiles/decode_rsa.py to decode private pem to pkcs1.
    'private_key':
EOF
python decode_rsa.py >> config.py
echo '}' >> config.py

# Create subscription
gcloud pubsub topics create $TOPIC --project=$PROJECT_ID
gcloud pubsub subscriptions create $TOPIC  --topic=$TOPIC --project=$PROJECT_ID
