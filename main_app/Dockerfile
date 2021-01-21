FROM ubuntu:18.04
      ENV FLASK_APP app.py
      ENV FLASK_RUN_HOST 0.0.0.0
      ENV LC_ALL C.UTF-8
      ENV LANG C.UTF-8
RUN apt-get update && apt-get install -y \
    python3 python3-pip mongodb
RUN pip3 install mongoengine flask celery blinker pytest pytest-dependency requests
EXPOSE 5000
RUN mkdir /main_app
COPY documents /main_app/documents
COPY notification_messages.py /main_app/documents
COPY /main_app/server.py /main_app/
COPY /main_app/start.sh /main_app/start.sh
COPY test.py /main_app/test.py
RUN mkdir /celery_app
RUN touch /celery_app/__init__.py
COPY /celery_app/celery.py /celery_app/
COPY /celery_app/tasks.py /celery_app/


