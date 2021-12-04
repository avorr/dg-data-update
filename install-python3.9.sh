#!/usr/bin/bash

curl -vk -O https://www.python.org/ftp/python/3.9.9/Python-3.9.9.tar.xz
tar -xf Python-3.9.9.tar.xz
mv Python-3.*/* .
yum -y install gcc make > /dev/null && yum clean all > /dev/null
Python-3.9.9/configure --enable-optimizations > /dev/null
make altinstall