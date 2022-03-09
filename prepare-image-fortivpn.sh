#!/usr/bin/bash

{
  apt-get update
  apt-get install -y python3 \
                     python3-pip \
                     screen \
                     openfortivpn

  pip3 install --no-cache --upgrade requests pymongo
} &> /dev/null

#  iputils-ping \
#tar -xf python3.9.9.tar
#tar -C / -xapf python3.9.9.tar.gz
#tar -xf venv.tar.gz