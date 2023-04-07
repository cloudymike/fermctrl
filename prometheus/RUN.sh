#!/bin/bash

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


${PROMETHEUSDIR}/prometheus --config.file=./prometheus.yml

