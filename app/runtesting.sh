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

# Clean out old container images
./dockerclean.sh

# Start mqtt
pushd mosquitto
$DOCKERCOMPOSE up -d --build
popd

# Run docker compose with rebuild
# Note that newer version it is docker compose, older docker-compose
$DOCKERCOMPOSE up --build

pushd mosquitto
$DOCKERCOMPOSE down
popd
