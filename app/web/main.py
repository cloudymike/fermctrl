from flask import Flask, render_template, Response, request
from flask_wtf import FlaskForm
from wtforms import IntegerField, SubmitField, RadioField
from wtforms.validators import DataRequired,Optional
import sys
import os
import config
import json

from concurrent.futures import TimeoutError

import redis

from prometheus_client import Gauge, generate_latest

import prometheus_client


# If `entrypoint` is not defined in app.yaml, App Engine will look for an app
# called `app` in `main.py`.
app = Flask(__name__)
# Required for forms
app.config['SECRET_KEY'] = 'cEumZnHA5QvxVDNXfazEDs7e6Eg368yD'

REDIS_SERVER = os.getenv('REDIS_SERVER', 'localhost')
datastore = redis.Redis(host=REDIS_SERVER, port=6379, decode_responses=True)

datastore.set('CurrentDevice',config.device_name)

# Initialize prometheus
prometheus_client.REGISTRY.unregister(prometheus_client.GC_COLLECTOR)
prometheus_client.REGISTRY.unregister(prometheus_client.PLATFORM_COLLECTOR)
prometheus_client.REGISTRY.unregister(prometheus_client.PROCESS_COLLECTOR)

actual_temperature=Gauge('actual_temperature','Actual Temperature',['device_name'])
target_temperature=Gauge('target_temperature','Target Temperature',['device_name'])
current_day=Gauge('current_day','Day in fermentation',['device_name'])
#actual_temperature=Gauge('actual_temperature','Actual Temperature')

# Initialize labels
# Use devices i config to avoid raceconditions
for device_name in config.device_list:
    actual_temperature.labels(device_name=device_name)
    target_temperature.labels(device_name=device_name)
    current_day.labels(device_name=device_name)


################### Form classes ###################
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

# Form to set the device
class deviceForm(FlaskForm):

    deviceList = datastore.lrange('DeviceList',0,999)
    print('deviceList in deviceForm{}'.format(deviceList))
    choicesList = []
    for deviceName in deviceList:
        choicesList.append((deviceName,deviceName))
    device = RadioField('Device', choices=choicesList)
    submit = SubmitField('Select')

#################### Helper functions ###################
def getStatus():
    deviceName = datastore.get('CurrentDevice')

    return(
        datastore.get('{}:TEMPERATURE'.format(deviceName)), 
        datastore.get('{}:TARGET'.format(deviceName)),
        datastore.get('{}:DAY'.format(deviceName)),
        datastore.hgetall('{}:PROFILE'.format(deviceName))
        )

def getStatusValue(status,device_name):
    value=datastore.get('{}:{}'.format(device_name,status))
    if value is None:
        value = 0
    return(value)

################### routes ###################
@app.route('/')
@app.route('/index')
def index():
    """Return a friendly HTTP greeting."""
    return render_template('index.html', title='Home page',device_name=datastore.get('CurrentDevice'))

@app.route('/graph')
def graph():
    prom_url = "http://{}:9090/graph?g0.expr=%7Bdevice_name%3D~%22{}%22%7D%20%20%20&g0.tab=0&g0.stacked=0&g0.show_exemplars=0&g0.range_input=12h".format(request.remote_addr, datastore.get('CurrentDevice'))
    print(prom_url)
 
    return render_template('graph.html', title='Graph',device_name=datastore.get('CurrentDevice'), frame_url=prom_url)


@app.route('/profile', methods=['GET', 'POST'])
def setProfile():

    deviceName = datastore.get('CurrentDevice')
    PROFILEnew=datastore.hgetall('{}:PROFILEnew'.format(deviceName))

    print("PROFILEnew {}.".format(PROFILEnew))

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

        datastore.delete('{}:PROFILEnew'.format(deviceName))
        datastore.hset('{}:PROFILEnew'.format(deviceName), mapping=profile)

        datastore.set('{}:UpdateProfile'.format(deviceName), 'TRUE')

    SORTED_PROFILE_DAYSnew = sorted(PROFILEnew, key=int)

    return render_template('profile.html', 
        title='Set Profile', 
        form=form, 
        sorted_profile_days=SORTED_PROFILE_DAYSnew,
        profile=PROFILEnew,
        device_name=datastore.get('CurrentDevice')
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
        profile=PROFILE,
        device_name=datastore.get('CurrentDevice')
        )


@app.route('/device', methods=['GET', 'POST'])
def setDevice():
    form = deviceForm(device=datastore.get('CurrentDevice'))
    if form.validate_on_submit():
        print('Got device {}'.format(form.device.data))

        device = str(form.device.data)
        datastore.set('CurrentDevice',  device.encode("utf-8"))

    return render_template(
        'device.html', 
        title='Device', 
        form=form,
        device_name=datastore.get('CurrentDevice')
        )


@app.route('/metrics')
def clientmetrics():
    deviceList = datastore.lrange('DeviceList',0,999)
    for device_name in deviceList:
        actual_temperature.labels(device_name=device_name).set( getStatusValue('TEMPERATURE',device_name))
        target_temperature.labels(device_name=device_name).set( getStatusValue('TARGET',device_name))
        current_day.labels(device_name=device_name).set( getStatusValue('DAY',device_name))


    return generate_latest()


#################### Main section. ###################
# Host 0.0.0.0 makes it available on the network, may not be a safe thing
#    change to 127.0.0.1 to be truly local
# Note,this is now handled in flask command in docker-compose and runweb.sh

app.run(host='0.0.0.0', port=8081)
