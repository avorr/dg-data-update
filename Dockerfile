#FROM python:3-alpine
FROM base.sw.sbc.space/base/redhat/rhel7:4.5-433

#RUN pip3 install --no-cache --upgrade requests pymongo

COPY . /opt/

#CMD ["/usr/local/bin/python3", "/opt/main.py"]