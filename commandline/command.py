#!/usr/bin/env python

import sys
sys.path.append('..')
import gcloudconfig.config

from google.cloud import iot_v1
import argparse

project_id = gcloudconfig.config.google_cloud_config['project_id']
cloud_region = gcloudconfig.config.google_cloud_config['cloud_region']
registry_id = gcloudconfig.config.google_cloud_config['registry_id']
device_id = gcloudconfig.config.google_cloud_config['device_id']


parser = argparse.ArgumentParser(description='Execute a command to device')
parser.add_argument('temperature', type=int, help='Set a temperature')
args = parser.parse_args()

client = iot_v1.DeviceManagerClient()
device_path = client.device_path(project_id, cloud_region, registry_id, device_id)

command = str(args.temperature)
data = command.encode("utf-8")

result = client.send_command_to_device(
    request={"name": device_path, "binary_data": data}
)
