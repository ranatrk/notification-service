# Notifications Service

This project manages notifications being sent to an API service regarding user and rides and accordingly saves/retrieves the data from a `mongodb` database. Upon changes in some of the attributes in the database triggers are fired to send notifications to a service that should handle forwarding them to the user either through push notifications or sms messages. The notification sending service it self isnt handled but is just simulated as log messages with the required data.

## Components
### Mongodb
Database used for the backend.

### Rabbitmq
Message Queue used by Celery to queue notifications to be handeled by Celery tasks

### Celery
Task queue that uses rabbitmq message broker. It is used to distribute the notification handelling across different tasks.
- Celery worker runs in this service
- Celery tasks are defined here indicating what to be done with the notifications. Since no real integration with providers is done, this is simply logged indicating the language, groups, messages, and the numbers/ids to be later used in the integration

### Main app
- Flask server with API endpoints to recieve app updates to the backend from external services e.g. the mobile application (/main_app/server.py)
- Mongoengine which is a python object data mapper for mongodb, is used to handle any database changes.The documents and schema are defined here.
- Signals is used with mongoengine to handle triggers when certain changes occur in the database.
- A file `notifications_messages.py` with Enums for the notifications in different languages is used here and also in the Celery service when showing different messages in the required language.

### Running
To build and run : `docker-compose up --build`

### Tests
To run tests: ` docker-compose run main_test pytest test.py`


