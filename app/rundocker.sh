#!/bin/bash

cp ../config/config.py web
cp ../config/config.py mqttrw

# Clean out old container images
./dockerclean.sh

# Run docker compose with rebuild
# Note that newer version it is docker compose, older docker-compose
docker-compose up --build
