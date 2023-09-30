FROM grafana/grafana-enterprise
ADD grafana.ini /etc/grafana/grafana.ini
ADD prometheus.yaml /etc/grafana/provisioning/datasources/prometheus.yaml
ADD fermctrldashboards.yaml /etc/grafana/provisioning/dashboards/fermctrldashboards.yaml
ADD fermctrlvar.json /var/lib/grafana/dashboards/fermctrlvar.json


