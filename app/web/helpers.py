import redis



#################### Helper functions ###################
def getStatus(datastore):
    deviceName = datastore.get('CurrentDevice')

    print("getStatus: {}".format(datastore.hgetall('{}:PROFILE'.format(deviceName))))
    return(
        datastore.get('{}:TEMPERATURE'.format(deviceName)), 
        datastore.get('{}:BUBBLECOUNT'.format(deviceName)), 
        datastore.get('{}:HEAT'.format(deviceName)), 
        datastore.get('{}:COOL'.format(deviceName)), 
        datastore.get('{}:TARGET'.format(deviceName)),
        datastore.get('{}:DAY'.format(deviceName)),
        datastore.hgetall('{}:PROFILE'.format(deviceName))
        )

def getStatusValue(datastore,status,device_name):
    value=datastore.get('{}:{}'.format(device_name,status))
    if value is None:
        value = 0
    print("status: {}".format(status,value))
    return(value)


