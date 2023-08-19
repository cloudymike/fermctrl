#!/bin/bash

cd prometheus

cp ../../config/config.py .
python3 -m venv venv
source venv/bin/activate
pip install  -r requirements.txt
python buildPrometheus.py 



PROMETHEUSVERSION=2.37.6
PROMETHEUSDIR=prometheus-${PROMETHEUSVERSION}.linux-amd64
if [ -d "${PROMETHEUSDIR}" ]
then
	echo prometheus is installed
else
	echo Installing prometheus version ${PROMETHEUSVERSION}
    wget https://github.com/prometheus/prometheus/releases/download/v${PROMETHEUSVERSION}/${PROMETHEUSDIR}.tar.gz
    tar xvzf ${PROMETHEUSDIR}.tar.gz
fi


${PROMETHEUSDIR}/prometheus --config.file=./prometheus_local.yml

