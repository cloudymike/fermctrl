#Creating new project id's is a bad things as it takes 30 days to remove them
#PROJECTID=$(python -c "from coolname import generate_slug; x=generate_slug(2); print(x)")
PROJECT_ID=myproject
REGION='us-central1'
REGISTRY_ID=tempctrl
DEVICE_ID=esp32tempctrl
TOPIC=tempctrltopic
STATE_PUBSUB_TOPIC=tempctrlstate
