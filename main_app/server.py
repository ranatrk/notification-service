import flask
from flask import request,Response
import json
from datetime import datetime

from documents.NotificationsMongoEngine import NotificationsMongoEngine
from documents.UserRide import UserRide


notifications_mongo_engine = NotificationsMongoEngine()

app = flask.Flask(__name__)

@app.route('/user/<user_id>', methods=['GET'])
def get_user(user_id):
    """
    get a user if found given the user id
    url params : user_id
    """
    user_mongo = notifications_mongo_engine.find_user(user_id)
    if user_mongo:
        user_json = user_mongo.to_json()
        return user_json
    else:
        return Response("User not found",status=400)

@app.route('/users', methods=['GET'])
def get_users():
    """
    get all users
    """
    users = notifications_mongo_engine.get_users()
    return users.to_json()

@app.route('/route/<route_id>', methods=['GET'])
def get_route(route_id):
    """
    get a route with route id
    url params: route_id
    """
    route_mongo = notifications_mongo_engine.find_route(route_id)
    if route_mongo:
        route_json = route_mongo.to_json()
        return route_json
    else:
        return Response("Route not found",status=400)

@app.route('/routes', methods=['GET'])
def get_routes():
    """
    get all routes
    """
    routes = notifications_mongo_engine.get_routes()
    return routes.to_json()

@app.route('/ride/<ride_id>', methods=['GET'])
def get_ride(ride_id):
    """
    get a ride with ride id
    url params: ride_id
    """
    ride_mongo = notifications_mongo_engine.find_ride(ride_id)
    if ride_mongo:
        ride_json = ride_mongo.to_json()
        return ride_json
    else:
        return Response("Ride not found",status=400)


@app.route('/rides', methods=['GET'])
def get_rides():
    """
    get all rides
    """
    rides = notifications_mongo_engine.get_rides()
    return rides.to_json()

@app.route('/route', methods=['POST'])
def add_route():
    """
    add/update a route with route id
    json params:route_id:str,
                start_point:str,
                end_point:str,
                stops:[str]
    """
    request_json = request.get_json()
    route_id = request_json.get('route_id',None)
    start_point = request_json.get('start_point',None)
    end_point = request_json.get('end_point',None)
    stops = request_json.get('stops',None)

    route_mongo = notifications_mongo_engine.add_route(route_id=route_id,start_point=start_point,end_point=end_point,stops=stops)
    if route_mongo:
        return route_mongo.to_json()
    else:
        return Response("Couldn't add route",status=400)


@app.route('/user', methods=['POST'])
def add_user():
    """
    add/update a user
    request params:user_id:str,
                   name:str,
                   email:str,
                   phone:str
    """
    request_json = request.get_json()
    user_id = request_json.get('user_id',None)
    name = request_json.get('name',None)
    email = request_json.get('email',None)
    phone = request_json.get('phone',None)
    language = request_json.get('language',None)

    user = notifications_mongo_engine.add_user(user_id=user_id,name=name,email=email,phone=phone,language=language)
    if user:
        return user.to_json()
    else:
        return Response("User not found",status=400)


@app.route('/ride', methods=['POST'])
def add_ride():
    """
    add a ride with ride id
    json params:ride_id:str,
                route_id:str
    """
    request_json = request.get_json()
    ride_id = request_json.get('ride_id',None)
    route_id = request_json.get('route_id',None)
    route = notifications_mongo_engine.find_route(route_id)
    if not route:
        return Response("Route not found",status=400)
    ride = notifications_mongo_engine.add_ride(ride_id=ride_id,route_id=route_id,ongoing=False,current_stop=None,users=None)
    if not ride:
        return Response("Ride not found",status=400)
    else:
        return ride.to_json()

@app.route('/ride/start/<ride_id>', methods=['POST'])
def start_ride(ride_id):
    """
    start a ride with ride id
    url params : ride_id:str
    triggers single custom notification sent to users in ride that the ride started
    """
    ride_mongo = notifications_mongo_engine.find_ride(ride_id)
    route_id = ride_mongo.route_id
    route_mongo = notifications_mongo_engine.find_route(route_id)
    current_stop = route_mongo.start_point

    updated_ride = notifications_mongo_engine.update_ride(ride_id=ride_id,route_id=route_id,ongoing=True,current_stop=current_stop)
    if not updated_ride:
        return Response("Ride not found",status=400)
    else:
        return updated_ride.to_json()

@app.route('/ride/next_stop/<ride_id>', methods=['POST'])
def next_stop(ride_id):
    """
    move to next stop for ride with ride id
    url params : ride_id:str
    triggers group push notifications to users in the ride grouped by the language they use
    """
    ride_mongo = notifications_mongo_engine.find_ride(ride_id)
    if not ride_mongo.ongoing:
        return Response("Ride not ongoing",status=400)
    current_stop = ride_mongo.current_stop

    route_id = ride_mongo.route_id
    route_mongo = notifications_mongo_engine.find_route(route_id)
    if current_stop == route_mongo.end_point:
        for user_ride in ride_mongo.users:
            if user_ride.onboard:
                user_ride.completed = True
                user_ride.onboard = False
        updated_ride = notifications_mongo_engine.update_ride(ride_id=ride_id,route_id=route_id,ongoing=False,current_stop=current_stop,users=ride_mongo.users)
    else:
        current_stop_index = route_mongo.stops.index(current_stop)
        next_stop = route_mongo.stops[current_stop_index+1]
        updated_ride = notifications_mongo_engine.update_ride(ride_id=ride_id,route_id=route_id,ongoing=ride_mongo.ongoing,current_stop=next_stop)
    if not updated_ride:
        return Response("Ride not found",status=400)
    else:
        return updated_ride.to_json()


@app.route('/ride/add_user', methods=['POST'])
def add_user_ride():
    """
    add a user to a ride
    json params:user_id:str,
                ride_id:str,
                start_point:str,
                end_point:str
    """
    request_json = request.get_json()
    ride_id = request_json.get('ride_id',None)
    user_id = request_json.get('user_id',None)
    start_point = request_json.get('start_point',None)
    end_point = request_json.get('end_point',None)

    ride = notifications_mongo_engine.find_ride(ride_id)
    user = notifications_mongo_engine.find_user(user_id)
    if not ride:
        return Response(f"Ride with id {ride_id} not found",status=400)
    if not user:
        return Response(f"User with id {user_id} not found",status=400)

    ride = notifications_mongo_engine.add_user_ride(user_id=user_id, ride_id=ride_id,start_point=start_point,end_point=end_point,onboard=False,completed=False)
    if not ride:
        return Response("Error occurred",status=400)
    else:
        return ride.to_json()

@app.route('/ride/user_onboard', methods=['POST'])
def update_user_to_onboard():
    """
    change user status to onboard
    json params:ride_id:str,
           user_id:str
    """
    request_json = request.get_json()
    ride_id = request_json.get('ride_id',None)
    user_id = request_json.get('user_id',None)

    ride = notifications_mongo_engine.find_ride(ride_id)
    if not ride:
        return Response("Ride not found",status=400)
    if not ride.ongoing:
        return Response("Ride not currently ongoing to add user onboard",status=400)
    for user_ride in ride.users:
        if user_ride.user.user_id == user_id:
            user_ride.onboard = True
    ride = notifications_mongo_engine.update_ride(ride_id=ride.ride_id,route_id=ride.route_id,ongoing=ride.ongoing,current_stop=ride.current_stop,users=ride.users)
    if not ride:
        return Response("Error occurred",status=400)
    else:
        return ride.to_json()

@app.route('/ride/user_offboard', methods=['POST'])
def update_user_to_offboard():
    """
    change user status to onboard False when leaving ride
    json params:ride_id:str,
           user_id:str
    """
    request_json = request.get_json()
    ride_id = request_json.get('ride_id',None)
    user_id = request_json.get('user_id',None)

    ride = notifications_mongo_engine.find_ride(ride_id)
    if not ride.ongoing:
        return Response("Ride not currently ongoing to add user onboard",status=400)
    for user_ride in ride.users:
        if user_ride.user.user_id == user_id:
            user_ride.onboard = False
            user_ride.completed = True
    ride = notifications_mongo_engine.update_ride(ride_id=ride.ride_id,route_id=ride.route_id,ongoing=ride.ongoing,current_stop=ride.current_stop,users=ride.users)
    if not ride:
        return Response("Error occurred",status=400)
    else:
        return ride.to_json()


@app.route('/notifications/sms', methods=['POST'])
def send_sms_notifications():
    """
    send sms notifications to either grouped users or custom filtered ones
    - grouping is done using the language of the user where they will recieve promo codes when this endpoint is called based on the language they use.
    - custom notifications send promo codes to each individual user seperately based on a param number_of_rides, if they completed it they recieve the promo code sms

    json params:sms_type:str ["group","custom"]
                number_of_rides:int (used only with custom sms type)
    """
    request_json = request.get_json()
    sms_type = request_json.get('sms_type',None)
    if sms_type == "group":
        notifications_mongo_engine.send_group_sms_phones()
        return "Request sent to send group sms grouped by languages"
    elif sms_type == "custom":
        number_of_rides = request_json.get('number_of_rides',None)
        notifications_mongo_engine.send_custom_sms_phones(int(number_of_rides))
        return f"Request sent to send custom sms for users that completed {number_of_rides}"
    else:
        return Response("SMS Type not supported. Can only be group or custom",status=400)


@app.route('/notifications/sms/<user_id>', methods=['GET'])
def get_notifications_sms(user_id):
    """
    get all sms notifications for a user given the user_id
    url params: user_id:str
    """
    notifications = notifications_mongo_engine.get_notifications(user_id,"sms")
    return notifications.to_json()

@app.route('/notifications/push/<user_id>', methods=['GET'])
def get_notifications_push(user_id):
    """
    get all push notifications for a user given the user_id
    url params: user_id:str
    """
    notifications = notifications_mongo_engine.get_notifications(user_id,"push")
    return notifications.to_json()


app.run(host="0.0.0.0")
