# Authentication problems with 10.2 Lock to 10.1.5 for now.
FROM grafana/grafana:10.1.5
ADD grafana.ini /etc/grafana/grafana.ini
ADD prometheus.yaml /etc/grafana/provisioning/datasources/prometheus.yaml
ADD fermctrldashboards.yaml /etc/grafana/provisioning/dashboards/fermctrldashboards.yaml
ADD fermctrlvar.json /var/lib/grafana/dashboards/fermctrlvar.json


