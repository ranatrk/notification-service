from mongoengine import Document
from mongoengine.fields import StringField,FloatField,ListField,IntField
import mongoengine
import enum
mongoengine.connect('mongoengine_notifications', host='mongodb', port=27017)

LANGUAGES = ["English","French"]

class User(Document):
  user_id = StringField(required=True,primary_key=True)
  name = StringField(required=True)
  email = StringField(required=True)
  phone = StringField(required=True)
  language = StringField(required=True,default="English",choices=LANGUAGES)


