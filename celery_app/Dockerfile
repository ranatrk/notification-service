FROM ubuntu:18.04
      ENV LC_ALL C.UTF-8
      ENV LANG C.UTF-8
RUN apt-get update && apt-get install -y \
    python3 python3-pip
RUN pip3 install celery
RUN mkdir /celery_app
RUN touch /celery_app/__init__.py
COPY notification_messages.py /celery_app/
COPY /celery_app/celery.py /celery_app/
COPY /celery_app/tasks.py /celery_app/
COPY /celery_app/celery_start.sh /celery_app/

