#!/bin/bash

docker rm $(docker ps -aq)

KEEPpython=$(docker images --filter=reference='python:*' -q)
KEEPredis=$(docker images --filter=reference='redis:*' -q)
KEEPprometheus=$(docker images --filter=reference='prom/prometheus:*' -q)

IMAGED2REMOVE=$(docker images -q | grep -v $KEEPpython | grep -v $KEEPredis| grep -v $KEEPprometheus)
echo Images to remove $IMAGED2REMOVE

docker image rm $IMAGED2REMOVE
