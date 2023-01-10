
use_google = False

topic = "tempctrlproj/ferm1topic"
hostname = '127.0.0.1'

google_cloud_config = {
    'project_id':'tempctrlproj',
    'cloud_region':'us-central1',
    'registry_id':'tempctrl',
    'topic':'ferm1topic',
    'device_id':'esp32tempctrl',
    'mqtt_bridge_hostname':'mqtt.googleapis.com',
    'mqtt_bridge_port':8883
}
