#!/bin/bash

docker rm $(docker ps -aq)

KEEPpython=$(docker images --filter=reference='python:*' -q)
KEEPredis=$(docker images --filter=reference='redis:*' -q)

docker image rm  $(docker images -q | grep -v $KEEPpython | grep -v KEEPredis)
