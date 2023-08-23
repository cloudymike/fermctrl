#!/bin/bash

cp ../config/config.py web
cp ../config/config.py mqttrw

# Clean out old container images
./dockerclean.sh

# Start mqtt
pushd mosquitto
docker-compose up -d --build
popd

# Run docker compose with rebuild
# Note that newer version it is docker compose, older docker-compose
docker-compose up --build

pushd mosquitto
docker-compose down
popd
