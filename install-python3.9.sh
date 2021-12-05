#!/usr/bin/bash

{
    mv centos.repo /etc/yum.repos.d/
    curl -k -O https://www.python.org/ftp/python/3.9.9/Python-3.9.9.tar.xz
    tar -xf Python-3.9.9.tar.xz
    cd Python-3.9.9
    yum -y install gcc make && yum clean all
    ./configure --enable-optimizations
    make altinstall || true

} &> /dev/null
