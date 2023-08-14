#!/bin/bash

docker rm $(docker ps -aq)

KEEPERIMAGES=$(docker images --filter=reference='python:*' -q)

docker image rm  $(docker images -q | grep -v $KEEPERIMAGES)
