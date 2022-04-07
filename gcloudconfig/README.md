# Setting up gcloud

## Login
Start with logging in to your account
`gcloud auth login`

This will open a browser to login to your account.

After the login try to run a gcloud command, as example try to check the projects:
`gcloud projects list`

## Variables
Copy the variables.example.sh to variables.sh and update with the values
that matches your setup. If you are starting from scratch, you can probably use variables as
is. If you already have a project started use that project_id. To check if you have a project run
the command:
`gcloud projects list`

## Create a project
If you do not have a ready to go project create this next. Right now we create an app for each project, the
URL is
`https://PROJECT_ID.appspot.com`

Creating a lot of new project id's is a bad things as it takes 30 days to remove them.

To create project use
`./create_project.sh`

To delete a project (though it will take 30 days to happen..):
`./delete_project.sh`

# Create an app
Currently the app is a simple creation of one app per project. Use the following command:
`./create_app.sh`
To delete an app:
`./delete_app.sh`

# Create a device
This setups device and device registry with key and creates a config file that will be used
by app and esp32 board. Among other things this will generate the keypair to be  used
by mqtt to allow esp32 board and google app to communicate.

To create device use
`./create_device.sh`

To delete device use
`./delete_device.sh`

Note that this script also creates topics and subscriptions. These are kind of the same thing in mqtt but
not in gcloud. Note that a subscription expire after EXPIRATION_PERIOD, set to max 365 days.

# config.py
You should now have a file config.py. This file will NOT be checked in with the repo, so you may want to copy
it to a safe place. This file will be used by both app engine build and esp32 build to
link the two together.
