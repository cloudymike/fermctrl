from flask import Flask, render_template, Response, request, redirect
from flask_wtf import FlaskForm
from wtforms import IntegerField, SubmitField, RadioField, SelectField, StringField
from wtforms.validators import DataRequired,Optional
import sys
import os
import config
import json

from concurrent.futures import TimeoutError

import redis

from prometheus_client import Gauge, generate_latest

import prometheus_client

from fetchrecipe import recipeDictListBeersmith
import fetchrecipe

from helpers import getStatus, getStatusValue

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
bubble_count=Gauge('bubble_count','Bubble Count per minute',['device_name'])
heater_on=Gauge('heater_on','Heater is on (1)',['device_name'])
cooler_on=Gauge('cooler_on','Cooler is on (1)',['device_name'])
target_temperature=Gauge('target_temperature','Target Temperature',['device_name'])
current_day=Gauge('current_day','Day in fermentation',['device_name'])
finish_day=Gauge('finish_day','Last day of program',['device_name'])
clearingagent=Gauge('clearingagent','Day to add clearing agent',['device_name'])
dryhop1=Gauge('dryhop1','Day to add first dry hop',['device_name'])
dryhop2=Gauge('dryhop2','Day to add second dry hop',['device_name'])

# Initialize labels
# Use devices i config to avoid raceconditions
for device_name in config.device_list:
    actual_temperature.labels(device_name=device_name)
    bubble_count.labels(device_name=device_name)
    heater_on.labels(device_name=device_name)
    cooler_on.labels(device_name=device_name)
    target_temperature.labels(device_name=device_name)
    current_day.labels(device_name=device_name)
    finish_day.labels(device_name=device_name)
    clearingagent.labels(device_name=device_name)
    dryhop1.labels(device_name=device_name)
    dryhop2.labels(device_name=device_name)


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

    finishDay = IntegerField('finishDay', validators=[Optional()])
    clearingagent = IntegerField('clearingagent', validators=[Optional()])
    dryhop1 = IntegerField('dryhop1', validators=[Optional()])
    dryhop2 = IntegerField('dryhop2', validators=[Optional()])

    recipeName = StringField('recipeName', validators=[Optional()])

    submit = SubmitField('Set')

#################### Forms ###################

class recipeForm(FlaskForm):

    choicesList=fetchrecipe.fetch_choicelist()

    '''
    choicesList = []
    recipeList=recipeDictListBeersmith()
    print("Recipelist: {}".format(recipeList))
    for recipeDict in recipeList:
        recipeName=recipeDict["recipe_name"]
        recipeJson=json.dumps(recipeDict)
        choicesList.append((recipeJson,recipeName))
    '''

    recipeName = RadioField('Recipe', choices=choicesList)
    submit = SubmitField('Load Recipe')



################### routes ###################


@app.route('/recipe', methods=['GET', 'POST'])
def loadRecipe():
    deviceName=datastore.get('CurrentDevice')
    form = recipeForm(recipe=getStatusValue(datastore,'RecipeName',deviceName))
    # Here is where we update the choicelist dynamically
    # The function should be a list of tuples (recipenumber,recipenames)
    # form.recipeName.choices = fetchrecipe.recipeNumberNameList()
    # To test that this is the place
    #form.recipeName.choices = []

recipeDictListBeersmith

    if form.validate_on_submit():
        formRawData=form.recipeName.data
        print(formRawData)
        (recipe_number,recipe_name)=formRawData

        datastore.set('{}:RecipeName'.format(deviceName),  str(recipeDict["recipe_name"]))

        # with the recipe number (form.recipeName.data) get recipe from web
        # Then use this to load the recipe 



        '''
        recipeDict=json.loads(form.recipeName.data)
        print('Got recipe {}'.format(recipeDict))

        print(recipeDict["targetDay1"])
        print(str(recipeDict["targetDay1"]))


        profile = {}
        profile[str(recipeDict["targetDay0"])] = str(recipeDict["targetTemp0"])
        profile[str(recipeDict["targetDay1"])] = str(recipeDict["targetTemp1"])
        profile[str(recipeDict["targetDay2"])] = str(recipeDict["targetTemp2"])
        profile[str(recipeDict["targetDay3"])] = str(recipeDict["targetTemp3"])
        profile[str(recipeDict["targetDay4"])] = str(recipeDict["targetTemp4"])
        #datastore.set('{}:targetDay0'.format(deviceName),  int(recipeDict["targetDay0"]))
        #datastore.set('{}:targetTemp0'.format(deviceName),  round(float(recipeDict["targetTemp0"])))
        print("Profile in loadRecipe: {}".format(profile))
        # Update the new profile and set new to TRUE to force upload to device
        datastore.delete('{}:PROFILEnew'.format(deviceName))
        datastore.hset('{}:PROFILEnew'.format(deviceName), mapping=profile)
        datastore.set('{}:UpdateProfile'.format(deviceName), 'TRUE')
        '''


        # Load profile in to main profile directly
        # This is needed CHANGE as we load profile from device
        # PROFILEnew-> DEVICE->PROFILE in mqttrw
        #datastore.delete('{}:PROFILE'.format(deviceName))
        #datastore.hset('{}:PROFILE'.format(deviceName), mapping=profile)

    deviceName=datastore.get('CurrentDevice') 
    return render_template(
        'recipe.html', 
        title='Recipe', 
        current_device=deviceName,
        device_list=config.device_list,
        active_page='recipe',
        form=form,
        recipeName=getStatusValue(datastore,'RecipeName',deviceName)
        )



@app.route('/graph')
def graph():
    prom_url = "http://{}:3000/d/FERMCTRLVAR/fermctrlvar?orgId=1&refresh=1m&var-device={}".format(config.hostname, datastore.get('CurrentDevice'))
    print(prom_url)
        
    deviceName=datastore.get('CurrentDevice') 

    return render_template('graph.html', 
        title='Graph',
        frame_url=prom_url,
        current_device = deviceName,
        device_list=config.device_list,
        active_page='graph',
        recipeName=getStatusValue(datastore,'RecipeName',datastore.get('CurrentDevice'))
    )




@app.route('/profile', methods=['GET', 'POST'])
def setProfile():

    # Note that profile is stored on device
    # FinishDay is only stored in REDIS
    # As we add more non device data, we may want to break this out. Maybe.

    deviceName = datastore.get('CurrentDevice')
    finishDay = getStatusValue(datastore,'FinishDay',deviceName)
    clearingagent = getStatusValue(datastore,'Clearingagent',deviceName)
    dryhop1 = getStatusValue(datastore,'Dryhop1',deviceName)
    dryhop2 = getStatusValue(datastore,'Dryhop2',deviceName)
    recipeName = getStatusValue(datastore,'RecipeName',deviceName)

    # If it is just updated read from PROFILEnew, otherwise use PROFILE, read from device
    if datastore.get('{}:UpdateProfile'.format(deviceName)) == 'TRUE':
        PROFILEnew=datastore.hgetall('{}:PROFILEnew'.format(deviceName))
    else:
        PROFILEnew=datastore.hgetall('{}:PROFILE'.format(deviceName))

    print("PROFILEnew {}.".format(PROFILEnew))
    # If there is no profile, create an empty one
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
    
        print(profile)
        datastore.delete('{}:PROFILEnew'.format(deviceName))
        datastore.hset('{}:PROFILEnew'.format(deviceName), mapping=profile)

        datastore.set('{}:UpdateProfile'.format(deviceName), 'TRUE')

        if form.finishDay.data:
            finishDay  = form.finishDay.data
            datastore.set('{}:FinishDay'.format(deviceName),  finishDay)

        if isinstance(form.clearingagent.data, int):
            clearingagent  = form.clearingagent.data
            if clearingagent == "":
                clearingagent = 0
            datastore.set('{}:Clearingagent'.format(deviceName),  clearingagent)

        if isinstance(form.dryhop1.data, int):
            dryhop1  = form.dryhop1.data
            if dryhop1 == "":
                dryhop1 = 0
            datastore.set('{}:Dryhop1'.format(deviceName),  dryhop1)

        if isinstance(form.dryhop2.data, int):
            dryhop2  = form.dryhop2.data
            if dryhop2 == "":
                dryhop2 = 0
            datastore.set('{}:Dryhop2'.format(deviceName),  dryhop2)

        if form.recipeName.data:
            recipeName = form.recipeName.data
            datastore.set('{}:RecipeName'.format(deviceName),  recipeName)

        # Read back to get the new profile
        PROFILEnew=datastore.hgetall('{}:PROFILEnew'.format(deviceName))

    SORTED_PROFILE_DAYSnew = sorted(PROFILEnew, key=int)

    return render_template('profile.html', 
        title='Set Profile', 
        form=form, 
        sorted_profile_days=SORTED_PROFILE_DAYSnew,
        profile=PROFILEnew,
        finishDay=finishDay,
        clearingagent=clearingagent,
        dryhop1=dryhop1,
        dryhop2=dryhop2,
        recipeName=recipeName,
        current_device = deviceName,
        device_list=config.device_list,
        active_page='profile'
        )

@app.route('/')
@app.route('/index')
@app.route('/displaytemp')
def displayTemp():

    TEMPERATURE,BUBBLECOUNT,HEAT,COOL,TARGET,DAY,PROFILE = getStatus(datastore)
    print("DisplayTemp: {}".format(PROFILE))
    SORTED_PROFILE_DAYS = sorted(PROFILE, key=int)

    device_name=datastore.get('CurrentDevice')

    return render_template('displaytemp.html', title='Status',
        temperature=TEMPERATURE,
        bubblecount=BUBBLECOUNT,
        heat=HEAT,
        cool=COOL,
        target=TARGET,
        day=DAY,
        finishDay=getStatusValue(datastore,'FinishDay',device_name),
        clearingagent=getStatusValue(datastore,'Clearingagent',device_name),
        dryhop1=getStatusValue(datastore,'Dryhop1',device_name),
        dryhop2=getStatusValue(datastore,'Dryhop2',device_name),
        sorted_profile_days=SORTED_PROFILE_DAYS,
        profile=PROFILE,
        recipeName=getStatusValue(datastore,'RecipeName',device_name),
        device_list=config.device_list,
        current_device = device_name,
        active_page='displaytemp'
        )


@app.route('/set_current', methods=['POST'])
def set_current():
    name = request.form.get('name')
    datastore.set("CurrentDevice", name)
    ref = request.referrer or url_for('index')
    return redirect(ref)


@app.route('/metrics')
def clientmetrics():
    deviceList = datastore.lrange('DeviceList',0,999)
    for device_name in deviceList:
        actual_temperature.labels(device_name=device_name).set( getStatusValue(datastore,'TEMPERATURE',device_name))
        bubble_count.labels(device_name=device_name).set( getStatusValue(datastore,'BUBBLECOUNT',device_name))
        heater_on.labels(device_name=device_name).set( getStatusValue(datastore,'HEAT',device_name))
        cooler_on.labels(device_name=device_name).set( getStatusValue(datastore,'COOL',device_name))
        target_temperature.labels(device_name=device_name).set( getStatusValue(datastore,'TARGET',device_name))
        current_day.labels(device_name=device_name).set( getStatusValue(datastore,'DAY',device_name))
        finish_day.labels(device_name=device_name).set( getStatusValue(datastore,'FinishDay',device_name))
        caval= (int(getStatusValue(datastore,'Clearingagent',device_name)) != 0) and (int(getStatusValue(datastore,'Clearingagent',device_name)) <= int(getStatusValue(datastore,'DAY',device_name)))
        clearingagent.labels(device_name=device_name).set( caval)
        dh1val =  (int(getStatusValue(datastore,'Dryhop1',device_name)) != 0) and (int(getStatusValue(datastore,'Dryhop1',device_name)) <= int(getStatusValue(datastore,'DAY',device_name)))
        dryhop1.labels(device_name=device_name).set( dh1val )
        dh2val = (int(getStatusValue(datastore,'Dryhop2',device_name)) != 0) and (int(getStatusValue(datastore,'Dryhop2',device_name)) <= int(getStatusValue(datastore,'DAY',device_name)))
        dryhop2.labels(device_name=device_name).set( dh2val)
        #dryhop2.labels(device_name=device_name).set( getStatusValue(datastore,'Dryhop2',device_name))


    return generate_latest()


# Access to prometheus for deep diving
@app.route('/prometheus')
def prometheus():
    prom_url = "http://{}:9090/graph?g0.expr=%7Bdevice_name%3D~%22{}%22%7D%20%20%20&g0.tab=0&g0.stacked=0&g0.show_exemplars=0&g0.range_input=12h".format(config.hostname, datastore.get('CurrentDevice'))
    print(prom_url)

    return render_template('graph.html', title='Graph',device_name=datastore.get('CurrentDevice'), frame_url=prom_url)




#################### Main section. ###################
# Host 0.0.0.0 makes it available on the network, may not be a safe thing
#    change to 127.0.0.1 to be truly local
# Note,this is now handled in flask command in docker-compose and runweb.sh

app.run(host='0.0.0.0', port=8081)
