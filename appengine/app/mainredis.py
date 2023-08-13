from flask import Flask, render_template, Response
from flask_wtf import FlaskForm
from wtforms import IntegerField, SubmitField, RadioField
from wtforms.validators import DataRequired,Optional
import sys
import config
import json

from concurrent.futures import TimeoutError
import paho.mqtt.client as mqtt

import redis


# If `entrypoint` is not defined in app.yaml, App Engine will look for an app
# called `app` in `main.py`.
app = Flask(__name__)
# Required for forms
app.config['SECRET_KEY'] = 'cEumZnHA5QvxVDNXfazEDs7e6Eg368yD'

datastore = redis.Redis(host='127.0.0.1', port=6379, decode_responses=True)

# Form to create profile
# Should be a loop but could not figure out how.
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

################### mqtt section ###################
# Should be run in different loop / container
# Remove printstatement when finished. For now it is good debugging
def on_message(client, userdata, message):
    PROFILE = {}
    TEMPERATURE='? '
    TARGET='? '
    DAY='? '

    topic = message.topic
    try:
        data = json.loads(message.payload)
    except:
        data = {}
    print("message received ", data)
    print("message topic=", topic)
    print("message qos=",message.qos)
    print("message retain flag=",message.retain)
    print(type(data))
    print("Data dictionary {}".format(data))
    TEMPERATURE=str(data.get('temperature','?'))
    datastore.set('TEMPERATURE', TEMPERATURE)
    TARGET=str(data.get('target','?'))
    datastore.set('TARGET', TARGET)
    DAY=str(data.get('day','?'))
    datastore.set('DAY', DAY)
    PF=str(data.get('profile',str({})))
    PF_STR = PF.replace("\'", "\"")
    PROFILE = json.loads(PF_STR)
    datastore.delete('PROFILE')
    datastore.hset('PROFILE', mapping=PROFILE)
    print("Temperature:{}   Target:{}   Day:{}".format(TEMPERATURE,TARGET,DAY))
    print(f"Profile {PROFILE}.")

def send_data(data):
    global client
    if config.use_google:
        project_id = config.google_cloud_config['project_id']
        cloud_region = config.google_cloud_config['cloud_region']
        registry_id = config.google_cloud_config['registry_id']
        device_id = config.google_cloud_config['device_id']
        client = iot_v1.DeviceManagerClient()
        device_path = client.device_path(project_id, cloud_region, registry_id, device_id)
        result = client.send_command_to_device(request={"name": device_path, "binary_data": data})
    else:
        client.publish(config.app_topic,data)
################### mqtt section end ###################

def getStatus():
    return(
        datastore.get('TEMPERATURE'), 
        datastore.get('TARGET'),
        datastore.get('DAY'),
        datastore.hgetall('PROFILE')
        )

################### routes ###################
@app.route('/')
@app.route('/index')
def index():
    """Return a friendly HTTP greeting."""
    return render_template('index.html', title='Home page')


@app.route('/profile', methods=['GET', 'POST'])
def setProfile():
    PROFILEnew=datastore.hgetall('PROFILEnew')

    print("PROFILEnew:{}.".format(PROFILEnew))

    if len(PROFILEnew) == 0:
        PROFILEnew={"0": 0}
    print("PROFILEnew updated:{}.".format(PROFILEnew))

    print("In setProfile")
    profile = {}
    form = profileForm()
    if form.is_submitted():
        print('Day0 {}'.format(form.targetDay0.data))
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
        send_data(data)
        # cache the update until next read to not make if confusing
        PROFILEnew = json.loads(data)
        datastore.delete('PROFILEnew')
        datastore.hset('PROFILEnew', mapping=PROFILEnew)

    SORTED_PROFILE_DAYSnew = sorted(PROFILEnew, key=int)

    return render_template('profile.html', 
        title='Set Profile', 
        form=form, 
        sorted_profile_days=SORTED_PROFILE_DAYSnew,
        profile=PROFILEnew
        )

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


# Main section. Should probably be broken out as main but wait until mqtt removed
# Host 0.0.0.0 makes it available on the network, may not be a safe thing
#    change to 127.0.0.1 to be truly local
broker_address=config.hostname
print("creating new instance")
client = mqtt.Client("fermctrlwebserver") #create new instance
client.on_message=on_message #attach function to callback
print("connecting to broker on {}".format(broker_address))
client.connect(broker_address) #connect to broker
client.loop_start() #start the loop
print("Subscribing to topic",config.device_topic)
client.subscribe(config.device_topic)


app.run(host='0.0.0.0', port=8081)
