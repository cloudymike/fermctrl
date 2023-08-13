# Run with flask and mqtt app separate
You need to start both scripts:
* runnomqtt.sh (the flask app)
* runmqtt.sh (the mqtt reader and writer)



# Basic flask app on app engine.
This is obsolete as GOOGLE stopped their IOT mqtt offering

You may have to login to your google account
`gcloud auth login`

This is the google tutorial:
https://cloud.google.com/appengine/docs/standard/python3/quickstart

This is a very useful companion page that lists the gcloud commands that are useful to set things up:
https://medium.com/@dmahugh_70618/deploying-a-flask-app-to-google-app-engine-faa883b5ffab

## Setup service account credentials
export GOOGLE_APPLICATION_CREDENTIALS=~/secrets/gcloud/myproject.json
See https://cloud.google.com/pubsub/docs/building-pubsub-messaging-system#create_service_account_credentials

# Remove projects is a bad thing
They will be in delete mode for 30 days so during that time you can not add other projects. To see what you have in delete mode:

gcloud projects list --filter='lifecycleState:DELETE_REQUESTED'


## Read the logs of a appengine
gcloud app logs tail --project phrasal-talon-439
