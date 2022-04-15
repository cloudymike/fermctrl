# Copyright 2018 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# [START gae_python38_app]
# [START gae_python3_app]
from flask import Flask, render_template
from flask_wtf import FlaskForm
from wtforms import IntegerField, SubmitField, RadioField
from wtforms.validators import DataRequired
import sys
import config
import json

from concurrent.futures import TimeoutError
from google.cloud import pubsub_v1, iot_v1

TEMPERATURE='? '
TARGET='? '

# If `entrypoint` is not defined in app.yaml, App Engine will look for an app
# called `app` in `main.py`.
app = Flask(__name__)
app.config['SECRET_KEY'] = 'cEumZnHA5QvxVDNXfazEDs7e6Eg368yD'

class targetForm(FlaskForm):
    targetTemp = IntegerField('targetTemp', validators=[DataRequired()])
    submit = SubmitField('Set')

class cmdForm(FlaskForm):
    cmd = RadioField('Command', choices=[('stop','stop'),('run','run'),('pause','pause')])
    submit = SubmitField('Execute')

@app.route('/')
@app.route('/index')
def index():
    """Return a friendly HTTP greeting."""
    return render_template('index.html', title='Home page')

@app.route('/target', methods=['GET', 'POST'])
def setTarget():
    form = targetForm()
    if form.validate_on_submit():
        print('Got temperature {}'.format(form.targetTemp.data))
        project_id = config.google_cloud_config['project_id']
        cloud_region = config.google_cloud_config['cloud_region']
        registry_id = config.google_cloud_config['registry_id']
        device_id = config.google_cloud_config['device_id']
        client = iot_v1.DeviceManagerClient()
        device_path = client.device_path(project_id, cloud_region, registry_id, device_id)

        command = str(form.targetTemp.data)
        data = command.encode("utf-8")

        result = client.send_command_to_device(request={"name": device_path, "binary_data": data})

    return render_template('target.html', title='Target temp', form=form)

@app.route('/cmd', methods=['GET', 'POST'])
def setCmd():
    form = cmdForm()
    if form.validate_on_submit():
        print('Got command {}'.format(form.cmd.data))
        project_id = config.google_cloud_config['project_id']
        cloud_region = config.google_cloud_config['cloud_region']
        registry_id = config.google_cloud_config['registry_id']
        device_id = config.google_cloud_config['device_id']
        client = iot_v1.DeviceManagerClient()
        device_path = client.device_path(project_id, cloud_region, registry_id, device_id)

        command = str(form.cmd.data)
        data = command.encode("utf-8")

        result = client.send_command_to_device(request={"name": device_path, "binary_data": data})

    return render_template('cmd.html', title='Command', form=form)

@app.route('/displaytemp')
def displayTemp():

    # TODO(developer)
    project_id = config.google_cloud_config['project_id']

    # This one is not currently in the config file
    subscription_id = config.google_cloud_config['topic']
    # Number of seconds the subscriber should listen for messages
    timeout = 5.0

    subscriber = pubsub_v1.SubscriberClient()
    # The `subscription_path` method creates a fully qualified identifier
    # in the form `projects/{project_id}/subscriptions/{subscription_id}`
    subscription_path = subscriber.subscription_path(project_id, subscription_id)

    def callback(message):
        global TEMPERATURE
        global TARGET
        print(f"Received {message}.")
        TEMPERATURE=str(json.loads(message.data)['temperature'])
        try:
            TARGET=str(json.loads(message.data)['target'])
        except:
            TARGET = '?'
        print(f"Temperature {TEMPERATURE}.")
        print(f"Target {TARGET}.")
        message.ack()

    streaming_pull_future = subscriber.subscribe(subscription_path, callback=callback)
    print(f"Listening for messages on {subscription_path}..\n")

    # Wrap subscriber in a 'with' block to automatically call close() when done.
    with subscriber:
        try:
            # When `timeout` is not set, result() will block indefinitely,
            # unless an exception is encountered first.
            outstr = streaming_pull_future.result(timeout=timeout)
        except TimeoutError:
            streaming_pull_future.cancel()
    return render_template('displaytemp.html', title='Current', temperature=TEMPERATURE, target=TARGET)
    #return(TEMPERATURE)

if __name__ == '__main__':
    # This is used when running locally only. When deploying to Google App
    # Engine, a webserver process such as Gunicorn will serve the app. This
    # can be configured by adding an `entrypoint` to app.yaml.
    app.run(host='127.0.0.1', port=8080, debug=True)
# [END gae_python3_app]
# [END gae_python38_app]
