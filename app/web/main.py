from flask import Flask, render_template, Response
from flask_wtf import FlaskForm
from wtforms import IntegerField, SubmitField, RadioField
from wtforms.validators import DataRequired,Optional
import sys
import os
import config
import json

from concurrent.futures import TimeoutError

import redis


# If `entrypoint` is not defined in app.yaml, App Engine will look for an app
# called `app` in `main.py`.
app = Flask(__name__)
# Required for forms
app.config['SECRET_KEY'] = 'cEumZnHA5QvxVDNXfazEDs7e6Eg368yD'

REDIS_SERVER = os.getenv('REDIS_SERVER', 'localhost')
datastore = redis.Redis(host=REDIS_SERVER, port=6379, decode_responses=True)

datastore.set('CurrentDevice',config.device_name)

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


def getStatus():
    deviceName = datastore.get('CurrentDevice')

    return(
        datastore.get('{}:TEMPERATURE'.format(deviceName)), 
        datastore.get('{}:TARGET'.format(deviceName)),
        datastore.get('{}:DAY'.format(deviceName)),
        datastore.hgetall('{}:PROFILE'.format(deviceName))
        )

################### routes ###################
@app.route('/')
@app.route('/index')
def index():
    """Return a friendly HTTP greeting."""
    return render_template('index.html', title='Home page')


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


# Main section. 
# Host 0.0.0.0 makes it available on the network, may not be a safe thing
#    change to 127.0.0.1 to be truly local

app.run(host='0.0.0.0', port=8081)
