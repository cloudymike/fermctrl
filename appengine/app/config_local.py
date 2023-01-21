
use_google = False

project = "tempctrlproj"
device_name  = "lagercooler"
device_data = "esp32data"
app_data = "settings"
device_topic = "{}/{}/{}".format(project,device_name,device_data)
app_topic = "{}/{}/{}".format(project,device_name,app_data)
hostname = '192.168.62.241'

google_cloud_config = {
    'project_id':'tempctrlproj',
    'cloud_region':'us-central1',
    'registry_id':'tempctrl',
    'topic':'ferm1topic',
    'device_id':'esp32tempctrl',
    'mqtt_bridge_hostname':'mqtt.googleapis.com',
    'mqtt_bridge_port':8883
}
