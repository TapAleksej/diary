#!/usr/bin/env bash
docker ps -qa | xargs docker rm -f
docker images -qa | xargs docker rmi -f

docker ps -a
docker images