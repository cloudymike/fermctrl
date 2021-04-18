# Basic flask app on app engine.

This is the google tutorial:
https://cloud.google.com/appengine/docs/standard/python3/quickstart

This is a very useful companion page that lists the gcloud commands that are useful to set things up:
https://medium.com/@dmahugh_70618/deploying-a-flask-app-to-google-app-engine-faa883b5ffab


# Remove projects is a bad thing
They will be in delete mode for 30 days so during that time you can not add other projects. To see what you have in delete mode:

gcloud projects list --filter='lifecycleState:DELETE_REQUESTED'
