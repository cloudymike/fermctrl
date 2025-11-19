#!/bin/bash

# Note that newer version it is docker compose, older docker-compose
which docker-compose
if [ "$?" == "0" ]
then
	DOCKERCOMPOSE='docker-compose'
else
	DOCKERCOMPOSE='docker compose'
fi

cp ../config/config.py web
cp ../config/config.py mqttrw

# Create persistent directories
sudo rm -rf /var/tmp/prometheus
sudo mkdir -p /var/tmp/prometheus
sudo chown 65534:65534 /var/tmp/prometheus

sudo rm -rf /var/tmp/redis
sudo mkdir -p /var/tmp/redis
sudo chown 65534:65534 /var/tmp/redis

# Clean out old container images
./dockerclean.sh

# Run docker compose with rebuild
$DOCKERCOMPOSE up --build
