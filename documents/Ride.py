from mongoengine import *
import mongoengine
from mongoengine import signals
from .UserRide import UserRide
from .Route import Route
from .notifications_publisher_helper import ongoing_change_notifications,current_stop_change_notifications


mongoengine.connect('mongoengine_notifications', host='mongodb', port=27017)

class Ride(Document):
  ride_id = StringField(required=True,primary_key=True)
  ongoing = BooleanField(required=True)
  route_id = StringField(required=True)
  current_stop = StringField(required=True,default='')
  users = ListField(EmbeddedDocumentField(UserRide))

  meta = {'allow_inheritance': True}

  @classmethod
  def post_save(cls, sender, document, **kwargs):
    print("Post Save: %s" % document.ride_id)
    updates, removals = document._delta()
    if not updates:
      return
    ride_id = document.id
    ride = type(document).objects.get(ride_id=str(document.id))
    route = Route.objects.get(route_id=ride.route_id)
    if 'created' in kwargs and kwargs['created']:
      # new not updated
      return
    if 'ongoing' in updates:
      # Notifications for start of ride and end of ride for all users
      ongoing_change_notifications(ride,updates['ongoing'])

    if 'current_stop' in updates:
      # Notifications for changed stops (stops coming up or missed)
      current_stop_change_notifications(ride,route)


signals.post_save.connect(Ride.post_save, sender=Ride)
