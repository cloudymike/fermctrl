import config
import yaml
import sys


fr = open('prometheus_example.yml','r')
pconfig = yaml.safe_load(fr)
print(yaml.dump(pconfig))

sys.exit(1)

pc = {}
g={}
g['scrape_interval']='60s'
g['evaluation_interval']='60s'
pc['global']=g

pc['rule_files']={}

sc = []
sc.append({'jobname':config.device_name})
pc['rule_files']['scrape_configs']=sc

gauth={}
gauth['username']=config.grafana_username
gauth['password']=config.grafana_password
grafana = []
grafana.append({'basic_auth':gauth})
grafana.append({'url':config.grafana_url})
pc['remote_write'] = grafana

print(yaml.dump(pc))

fp = open('prometheus.yml', 'w')
yaml.dump(pc,fp)
