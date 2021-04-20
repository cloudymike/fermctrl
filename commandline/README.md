# Commandline to control device

Source setup.sh  to setup virtual environment and include required packages.
Then run each file as a command

## Initial command line with python

### command.py
Will send a command to the device. Currently the only command is the temperature to set.
Example:
```
./command.py 68
```


### subscribe.py
Will get all metrics from device, and try to clean queue
```
# ./subscriber.py 
Listening for messages on projects/tempctrlproj/subscriptions/ferm1topic..

Received Message {
  data: b'{"temperature":80.6}'
  ordering_key: ''
  attributes: {
    "deviceId": "esp32tempctrl",
    "deviceNumId": "2577321808646966",
    "deviceRegistryId": "tempctrl",
    "deviceRegistryLocation": "us-central1",
    "projectId": "tempctrlproj",
    "subFolder": ""
  }
}.
```
