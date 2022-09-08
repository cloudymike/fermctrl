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
from flask import Flask, render_template, Response
from flask_wtf import FlaskForm
from wtforms import IntegerField, SubmitField, RadioField
from wtforms.validators import DataRequired,Optional
import sys
import config
import json

from concurrent.futures import TimeoutError
from google.cloud import pubsub_v1, iot_v1

TEMPERATURE='? '
TARGET='? '
DAY='? '
PROFILE=[]

# If `entrypoint` is not defined in app.yaml, App Engine will look for an app
# called `app` in `main.py`.
app = Flask(__name__)
app.config['SECRET_KEY'] = 'cEumZnHA5QvxVDNXfazEDs7e6Eg368yD'

class targetForm(FlaskForm):
    targetTemp = IntegerField('targetTemp', validators=[DataRequired()])
    submit = SubmitField('Set')

class profileForm(FlaskForm):
    targetDay0 = IntegerField('targetDay0', validators=[DataRequired()])
    targetTemp0 = IntegerField('targetTemp0', validators=[Optional()])
    targetDay1 = IntegerField('targetDay1', validators=[Optional()])
    targetTemp1 = IntegerField('targetTemp1', validators=[Optional()])
    targetDay2 = IntegerField('targetDay2', validators=[Optional()])
    targetTemp2 = IntegerField('targetTemp2', validators=[Optional()])
    targetDay3 = IntegerField('targetDay3', validators=[Optional()])
    targetTemp3 = IntegerField('targetTemp3', validators=[Optional()])
    targetDay4 = IntegerField('targetDay4', validators=[Optional()])
    targetTemp4 = IntegerField('targetTemp4', validators=[Optional()])
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
    print("In setTarget")
    TEMPERATURE,TARGET,DAY,PROFILE = getStatus()
    form = targetForm()
    if form.validate_on_submit():
        print('Got temperature {}'.format(form.targetTemp.data))
        project_id = config.google_cloud_config['project_id']
        cloud_region = config.google_cloud_config['cloud_region']
        registry_id = config.google_cloud_config['registry_id']
        device_id = config.google_cloud_config['device_id']
        client = iot_v1.DeviceManagerClient()
        device_path = client.device_path(project_id, cloud_region, registry_id, device_id)

        profile = { 0: form.targetTemp.data}
        profileJSON = json.dumps(profile)
        print("Sending: {}".format(profileJSON))
        data = profileJSON.encode("utf-8")

        result = client.send_command_to_device(request={"name": device_path, "binary_data": data})

    return render_template('target.html', title='Target temp', form=form, target=TARGET)

@app.route('/profile', methods=['GET', 'POST'])
def setProfile():
    print("In setProfile")
    profile = {}
    form = profileForm()
    print(form)
    if form.is_submitted():
    #if form.validate_on_submit():
    #if True:
        print('Day0 {}'.format(form.targetDay0.data))
        project_id = config.google_cloud_config['project_id']
        cloud_region = config.google_cloud_config['cloud_region']
        registry_id = config.google_cloud_config['registry_id']
        device_id = config.google_cloud_config['device_id']
        client = iot_v1.DeviceManagerClient()
        device_path = client.device_path(project_id, cloud_region, registry_id, device_id)

        profile[str(form.targetDay0.data)] = form.targetTemp0.data
        if form.targetDay1.data and form.targetTemp1.data:
            profile[str(form.targetDay1.data)] = form.targetTemp1.data
        if form.targetDay2.data and form.targetTemp2.data:
            profile[str(form.targetDay2.data)] = form.targetTemp2.data
        if form.targetDay3.data and form.targetTemp3.data:
            profile[str(form.targetDay3.data)] = form.targetTemp3.data
        if form.targetDay4.data and form.targetTemp4.data:
            profile[str(form.targetDay4.data)] = form.targetTemp4.data

        profileJSON = json.dumps(profile)
        print("Sending: {}".format(profileJSON))
        data = profileJSON.encode("utf-8")
        result = client.send_command_to_device(request={"name": device_path, "binary_data": data})

    return render_template('profile.html', title='Set Profile', form=form)

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

def getStatus():

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
        global DAY
        global PROFILE
        print(f"Received {message}.")
        TEMPERATURE=str(json.loads(message.data)['temperature'])
        try:
            TARGET=str(json.loads(message.data)['target'])
        except:
            TARGET = '?'
        try:
            DAY=str(json.loads(message.data)['day'])
        except:
            DAY = '?'
        try:
            PF=str(json.loads(message.data)['profile'])
        except:
            PF = {}
        PF_STR = PF.replace("\'", "\"")
        PROFILE = json.loads(PF_STR)
        print(f"Temperature {TEMPERATURE}.")
        print(f"Target {TARGET}.")
        print(f"Day {DAY}.")
        print(f"Profile {PROFILE}.")
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
    return(TEMPERATURE, TARGET,DAY,PROFILE)

@app.route('/displaytemp')
def displayTemp():

    TEMPERATURE,TARGET,DAY,PROFILE = getStatus()

    SORTED_PROFILE_DAYS = sorted(PROFILE, key=int)

    return render_template('displaytemp.html', title='Current',
        temperature=TEMPERATURE,
        target=TARGET,
        day=DAY,
        sorted_profile_days=SORTED_PROFILE_DAYS,
        profile=PROFILE)

@app.route('/metrics')
def metrics():
    TEMPERATURE,TARGET,DAY,PROFILE = getStatus()

    metric_string="""# HELP Actual Temperature
# TYPE actual_temperature gauge
actual_temperature {}
# HELP Target Temperature
# TYPE target_temperature gauge
target_temperature {}
# HELP Day in fermentation
# TYPE fermentation_day counter
fermentation_day {}
""".format(TEMPERATURE, TARGET, DAY)

    return Response(metric_string, mimetype='text/plain')

if __name__ == '__main__':
    # This is used when running locally only. When deploying to Google App
    # Engine, a webserver process such as Gunicorn will serve the app. This
    # can be configured by adding an `entrypoint` to app.yaml.
    # Host 0.0.0.0 makes it available on the network, may not be a safe thing
    #    change to 127.0.0.1 to be truly local
    app.run(host='0.0.0.0', port=8080, debug=True)
# [END gae_python3_app]
# [END gae_python38_app]
