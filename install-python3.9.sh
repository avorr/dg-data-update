#!/usr/bin/bash

#{
#    mv centos.repo /etc/yum.repos.d/
#    curl -k -O https://www.python.org/ftp/python/3.9.9/Python-3.9.9.tar.xz
#    tar -xf Python-3.9.9.tar.xz
#    cd Python-3.9.9
#    yum -y install gcc make zlib-devel
#    ./configure --enable-optimizations
#    make altinstall || true
#    pip3.9 install requests pymongo
#
#} &> /dev/null

tar -xf python3.9.9.tar
tar -C / -xapf python3.9.9.tar.gz
tar -xf venv.tar.gz