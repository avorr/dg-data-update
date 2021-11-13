FROM python:3-alpine

RUN pip3 install --no-cache --upgrade requests

COPY . /opt/

#CMD ["/usr/local/bin/python3", "/opt/main.py"]