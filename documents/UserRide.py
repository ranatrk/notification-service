from mongoengine import *
from mongoengine import Document,ReferenceField
import mongoengine
from .User import User
mongoengine.connect('mongoengine_notifications', host='mongodb', port=27017)

class UserRide(EmbeddedDocument):
  user = ReferenceField(User)
  start_point = StringField(required=True)
  end_point = StringField(required=True)
  onboard = BooleanField(default=False)
  completed = BooleanField(default=False)

  meta = {'allow_inheritance': True}

