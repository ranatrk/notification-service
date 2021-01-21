from celery import Celery

app = Celery('celery_app',broker='amqp://guest:guest@rabbitmq//',include=["celery_app.tasks"])

if __name__ == '__main__':
    app.start()
