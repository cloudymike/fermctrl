# The app

## Run with flask and mqtt app separate
You need to start both scripts:
* runweb.sh (the flask app)
* runmqtt.sh (the mqtt reader and writer)
* runprometheus.sh (Prometheus colector)

In addition a redis server and a mosquitto server needs to run on localhost

## Run with docker compose

Remove container images that are build. Save some basics like redis and base python
`dockerclean.sh`

Bring up docker environment with a rebuild. Note that you may need to remove images to get a
clean rebuild
`docker-compose up --build`

## Run in testing mode
runtesting.sh

This mode includes a local mosquitto that allows a self contained environment for testing
May be useful as real environment, but some more testing needed.

## Ports
* web server -> 8081 Internal 5000
* prometheus -> 9090
* redis -> Internal  6379
* mosquitto -> 1883

## Prometheus expressions

Find all metrics for a device:
`{device_name=~"testcooler"}   `

Find a metric (actual_temperature) for all devices:
`actual_temperature`

Show just temperatures (actual and target) for one device
`{__name__=~"(actual|target)_temperature", device_name=~"alecooler"} `

We are starting to get into hacks here, and a better solution may be to use grafana

## Basic flask app on app engine.
This is obsolete as GOOGLE stopped their IOT mqtt offering

You may have to login to your google account
`gcloud auth login`

This is the google tutorial:
https://cloud.google.com/appengine/docs/standard/python3/quickstart

This is a very useful companion page that lists the gcloud commands that are useful to set things up:
https://medium.com/@dmahugh_70618/deploying-a-flask-app-to-google-app-engine-faa883b5ffab

### Setup service account credentials
export GOOGLE_APPLICATION_CREDENTIALS=~/secrets/gcloud/myproject.json
See https://cloud.google.com/pubsub/docs/building-pubsub-messaging-system#create_service_account_credentials

### Remove projects is a bad thing
They will be in delete mode for 30 days so during that time you can not add other projects. To see what you have in delete mode:

gcloud projects list --filter='lifecycleState:DELETE_REQUESTED'


### Read the logs of a appengine
gcloud app logs tail --project phrasal-talon-439
