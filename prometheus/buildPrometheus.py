import config
import yaml
import sys


fr = open('prometheus_example.yml','r')
pconfig = yaml.safe_load(fr)

pconfig['remote_write'] = [
    {
    	'url': config.grafana_url,
    	'basic_auth':
         {
         	'username': config.grafana_username,
         	'password': config.grafana_password
         }
    }
]
pconfig['scrape_configs'] = [ {
    'job_name': config.device_name, 
    'static_configs': [{'targets': ['localhost:8081']} ]
    } ]


fw = open('prometheus.yml', 'w')
yaml.dump(pconfig,fw)

