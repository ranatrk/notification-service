from mongoengine import *
import mongoengine
mongoengine.connect('mongoengine_notifications', host='mongodb', port=27017)

class SMSNotification(Document):
  notification_id = StringField(required=True,primary_key=True)
  message = StringField(required=True)
  # user_phones = ListField(required=True)
  user_id = StringField(required=True)
  notification_type = StringField(required=True,options=["group","custom"])
  time = DateTimeField(required=True)
  language = StringField(required=True,options=["English","French"])


