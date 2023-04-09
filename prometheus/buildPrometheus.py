import config
import yaml
import sys


fr = open('prometheus_example.yml','r')
pconfig = yaml.safe_load(fr)

#grafana = []
#gauth={}
#gauth['username']=config.grafana_username
#gauth['password']=config.grafana_password
#grafana.append({'basic_auth':gauth})
#grafana.append({'url':config.grafana_url})
#pconfig['remote_write'] = grafana

pconfig['remote_write'][0]= {'url': config.grafana_url}
pconfig['remote_write'].append({'basic_auth':{'username': config.grafana_password, 'password': config.grafana_password}})

#pconfig['rule_files']={}

sc = []

sc.append({'job_name':config.device_name})
sc.append({'static_configs':[{'targets': ['localhost:8081']}]})
pconfig['scrape_configs']=sc


fw = open('prometheus.yml', 'w')
yaml.dump(pconfig,fw)

print(yaml.dump(pconfig))

