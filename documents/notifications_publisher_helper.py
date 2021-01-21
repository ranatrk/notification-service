import string
import random
import datetime
import sys
sys.path.append('/')
from celery_app.tasks import notify_sms_group,notify_sms_single,notify_push_group,notify_push_single
from .SMSNotification import SMSNotification
from .PushNotification import PushNotification
from .notification_messages import English,French
LETTERS = string.ascii_letters


def _save_push_notification(message_id,extra,user_id,notification_type,language):
  """
  Save a push notification to database
  """
  if language == "English":
    message = English[message_id].value
  elif language == "French":
    message = French[message_id].value
  random_id = ''.join(random.choice(LETTERS) for i in range(10))
  push_notification = PushNotification(notification_id=random_id,message=message.format(extra),user_id=user_id,notification_type=notification_type,time=datetime.datetime.now,language=language)
  push_notification.save()

def ongoing_change_notifications(ride,ongoing_ride):
    """
    handle sending notifications to ride users when ongoing changes for a ride
    """
    user_rides = ride.users
    user_ids_dict = {}
    if ongoing_ride:
      message_id = "start"
    else:
      message_id = "end"

    for user_ride in user_rides:
      user_id = user_ride.user.user_id
      language = user_ride.user.language
      if language not in user_ids_dict:
        user_ids_dict[language] = [user_id]
      else:
        user_ids_dict[language].append(user_id)
      notify_push_single.delay(message_id,ride.ride_id,user_id,language)
      _save_push_notification(message_id,ride.ride_id,user_id,"custom",language)

    return

def current_stop_change_notifications(ride,route):
  user_rides = ride.users
  users_pickup = {}
  users_dropoff = {}
  for user_ride in user_rides:
    current_stop_index = route.stops.index(ride.current_stop)
    start_point_index = route.stops.index(user_ride.start_point)
    end_point_index = route.stops.index(user_ride.end_point)
    if current_stop_index + 1 == start_point_index:
      #  Pickup location coming up
      if user_ride.user.language not in users_pickup:
        users_pickup[user_ride.user.language] = [user_ride.user.user_id]
      else:
        users_pickup[user_ride.user.language].append(user_ride.user.user_id)
    elif start_point_index<current_stop_index and current_stop_index + 1 == end_point_index:
      # drop off coming up
      if user_ride.user.language not in users_dropoff:
        users_dropoff[user_ride.user.language] = [user_ride.user.user_id]
      else:
        users_dropoff[user_ride.user.language].append(user_ride.user.user_id)
  if users_pickup:
    message_id = "pickup"
    for language,user_ids in users_pickup.items():
      notify_push_group.delay(message_id,ride.ride_id,users_pickup[language],language)
      for user_id in user_ids:
        _save_push_notification(message_id,ride.ride_id,user_id,"group",language)

  if users_dropoff:
    message_id = "dropoff"
    for language,user_ids in users_dropoff.items():
      notify_push_group.delay(message_id,ride.ride_id,users_dropoff[language],language)
      for user_id in users_dropoff:
        _save_push_notification(message_id,ride.ride_id,user_id,"group",language)

def send_group_sms_notifications(phone_numbers_by_language):
  # {language:[phonenumbers]}
  for language,data in phone_numbers_by_language.items():
    phone_numbers = data["phone_numbers"]
    promo_code = ''.join(random.choice(LETTERS) for i in range(10))
    message_id = "save25"
    notify_sms_group.delay(message_id,promo_code,phone_numbers,language=language)

    for index,user_id in enumerate(data["user_ids"]):
      if language == "English": # message_id 5
        message = English[message_id].value
      elif language == "French":
        message = French[message_id].value
      random_id = ''.join(random.choice(LETTERS) for i in range(10))
      sms_notification = SMSNotification(notification_id=random_id,message=message.format(promo_code).format(promo_code),user_id=user_id,notification_type="group",time=datetime.datetime.now,language=language)
      sms_notification.save()

def send_custom_sms_notification(message,extra,phone_number,language):
  notify_sms_single.delay(message,extra,phone_number,language)
