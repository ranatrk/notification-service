from mongoengine import *
import mongoengine
mongoengine.connect('mongoengine_notifications', host='mongodb', port=27017)

class Route(Document):
  route_id = StringField(required=True,primary_key=True)
  start_point = StringField(required=True)
  end_point = StringField(required=True)
  stops = ListField(required=True)
