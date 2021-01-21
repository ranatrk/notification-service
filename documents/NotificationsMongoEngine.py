import random,datetime
from mongoengine import *
from .User import User
from .Ride import Ride
from .Route import Route
from .UserRide import UserRide
from .SMSNotification import SMSNotification
from .PushNotification import PushNotification
from .notifications_publisher_helper import send_group_sms_notifications,send_custom_sms_notification,LETTERS
from .notification_messages import English,French
connect('mongoengine_notifications', host='mongodb', port=27017)


class NotificationsMongoEngine():

  def add_user(self,user_id,name,email,phone,language):
    existing_user = User.objects.filter(user_id=user_id).clear_cls_query().first()
    if not existing_user:
      user = User(user_id=user_id,name=name,email=email,phone=phone,language=language)
    else:
      user = existing_user
      user.name = name or user.name
      user.email = email or user.email
      user.phone = phone or user.phone
      user.language = language or user.language
    user.save()
    return user

  def update_user(self,user_id,name=None,email=None,phone=None):
    existing_user = User.objects.filter(user_id=user_id).clear_cls_query().first()
    if not existing_user:
      return
    else:
      user = existing_user
      user.name = name or user.name
      user.email = email or user.email
      user.phone = phone or user.phone
      user.save()
    return user

  def find_user(self,user_id):
    return User.objects.filter(user_id=user_id).clear_cls_query().first()

  def add_ride(self,ride_id,route_id,ongoing,current_stop=None,users=None):
    ride = Ride.objects.filter(ride_id=ride_id).clear_cls_query().first()
    if not ride:
      ride = Ride(ride_id=ride_id,route_id=route_id,ongoing=ongoing,current_stop=current_stop,users=users)
    else:
      ride.ride_id= ride_id or ride.ride_id
      ride.route_id= route_id or ride.route_id
      ride.ongoing= ongoing
      ride.current_stop= current_stop or ride.current_stop
      ride.users= users or ride.users
    ride.save()
    return ride

  def update_ride(self,ride_id,route_id,ongoing,current_stop,users=None):
    ride = Ride.objects.filter(ride_id=ride_id).clear_cls_query().first()
    if not ride:
      return "Ride not found"

    ride.ride_id= ride_id or ride.ride_id
    ride.route_id= route_id or ride.route_id
    ride.ongoing= ongoing
    ride.current_stop= current_stop or ride.current_stop
    ride.users= users or ride.users
    ride.save()
    return ride

  def add_user_ride(self,user_id, ride_id,start_point,end_point,onboard=False,completed=False):
    ride = Ride.objects.filter(ride_id=ride_id).clear_cls_query().first()
    user = User.objects.filter(user_id=user_id).clear_cls_query().first()
    if not ride:
      return "Ride not found"
    if not user:
      return "Ride not found"
    user_ride = UserRide(user=user,start_point=start_point,end_point=end_point,onboard=onboard,completed=completed)
    ride.users.append(user_ride)
    ride.save()
    return ride

  def find_ride(self,ride_id):
    return Ride.objects.filter(ride_id=ride_id).clear_cls_query().first()

  def add_route(self,route_id,start_point,end_point,stops=None):
    existing_route = Route.objects.filter(route_id=route_id).clear_cls_query().first()
    if not existing_route:
      route = Route(route_id=route_id,start_point=start_point,end_point=end_point,stops=stops)
    else:
      route = existing_route
      route.route_id = route_id or route.route_id
      route.start_point = start_point or route.start_point
      route.end_point = end_point or route.end_point
      route.stops = stops or route.stops
    route.save()
    return route

  def update_route(self,route_id,start_point,end_point,stops=None):
    existing_route = Route.objects.filter(route_id=route_id).clear_cls_query().first()
    if not existing_route:
      return
    else:
      route = existing_route
      route.route_id = route_id or route.route_id
      route.start_point = start_point or route.start_point
      route.end_point = end_point or route.end_point
      route.stops = stops or route.stops
      route.save()
    return route

  def find_route(self,route_id):
    return Route.objects.filter(route_id=route_id).clear_cls_query().first()

  def get_users(self):
    return User.objects

  def get_routes(self):
    return Route.objects

  def get_rides(self):
    return Ride.objects

  def send_group_sms_phones(self):
    phone_numbers_by_language = {} # {language:{"phone_numbers":[phonenumbers],"user_ids":[user_ids]}
    for ride in Ride.objects:
      for user_ride in ride.users:
        if user_ride.user.language not in phone_numbers_by_language.keys():
          phone_numbers_by_language[user_ride.user.language] = {}
          phone_numbers_by_language[user_ride.user.language]["phone_numbers"] = [user_ride.user.phone]
          phone_numbers_by_language[user_ride.user.language]["user_ids"] = [user_ride.user.user_id]
        else:
          phone_numbers_by_language[user_ride.user.language]["phone_numbers"].append(user_ride.user.phone)
          phone_numbers_by_language[user_ride.user.language]["user_ids"].append(user_ride.user.user_id)
    send_group_sms_notifications(phone_numbers_by_language)



  def send_custom_sms_phones(self,number_of_rides):
    # Send sms if users completed number of rides
    # Not practical - example only
    users_sent =  []# {user_id:(phone_number,language)}
    ride_counter = {} # {userid:count}
    for ride in Ride.objects:
      for user_ride in ride.users:
        user_id = user_ride.user.user_id
        if user_id not in ride_counter.keys():
          ride_counter[user_id] = 0
        # For each user that was added to a ride add it to that users count
        # If the ride count for a user satisfied the number_of_rides, a single notifications is sent to them and saved in the database
        ride_counter[user_id] += 1
        if ride_counter[user_id] >= number_of_rides and user_id not in users_sent:
            users_sent.append(user_id)
            promo_code = ''.join(random.choice(LETTERS) for i in range(10))
            message_id = "save50"
            language = user_ride.user.language

            send_custom_sms_notification(message_id,promo_code,user_ride.user.phone,language)
            if language == "English":
              message = English[message_id].value
            elif language == "French":
              message = French[message_id].value
            random_id = ''.join(random.choice(LETTERS) for i in range(10))
            sms_notification = SMSNotification(notification_id=random_id,message=message.format(promo_code),user_id=user_id,notification_type="custom",time=datetime.datetime.now,language=user_ride.user.language)
            sms_notification.save()

  def get_notifications(self,user_id,type):
    if type == "sms":
      return SMSNotification.objects.filter(user_id=user_id)
    elif type == "push":
      return PushNotification.objects.filter(user_id=user_id)










