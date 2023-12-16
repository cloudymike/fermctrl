
use_google = False

project = "tempctrlproj"
device_name  = "testcooler"
device_list = [device_name, "lagercooler"]
device_data = "esp32data"
app_data = "settings"
device_topic = "{}/{}/{}".format(project,device_name,device_data)
app_topic = "{}/{}/{}".format(project,device_name,app_data)
hostname = '192.168.123.123'
