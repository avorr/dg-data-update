#!/bin/bash
docker build -f Dockerfile-forticlient . -t forti-docker
docker run -it --rm --name docker-forticlient --privileged --net host --env-file .env_PD20 -e HOST=37.18.109.130:18443 -e LOGIN=${FORTI_CRED_USR} -e PASSWORD=${FORTI_CRED_PSW} forti-docker
docker exec -it $(docker ps -aq -f "name=docker-forticlient") /usr/bin/python3 /opt/main.py