#!/usr/bin/bash

{
  apt-get update
  apt-get install curl -y
  curl https://filestore.fortinet.com/forticlient/downloads/FortiClientFullVPNInstaller_6.4.0.0851.deb -o FortiClientFullVPNInstaller_6.4.0.0851.deb
  apt-get install ./FortiClientFullVPNInstaller_6.4.0.0851.deb -y

  apt-get install -y -o APT::Install-Recommends=false -o APT::Install-Suggests=false \
  ca-certificates \
  iproute2 \
  python3 \
  expect \
  screen
  pip3 install --no-cache --upgrade requests

#  iputils-ping \
} &> /dev/null

#tar -xf python3.9.9.tar
#tar -C / -xapf python3.9.9.tar.gz
#tar -xf venv.tar.gz
