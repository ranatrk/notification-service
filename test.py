import requests
import pytest
from pytest_dependency import depends
from unittest import TestCase

BASE_URL = 'http://main_app:5000'


class Test(TestCase):
  @classmethod
  def teardown_class(cls):
    from pymongo import MongoClient
    client = MongoClient("mongodb", 27017)
    client.drop_database('mongoengine_notifications')

  @pytest.mark.dependency(name="testa_add_user")
  def testa_add_user(self):
    # Add a new user
    user_url = f"{BASE_URL}/user"
    user_data = {"user_id":"test1user",
                "name":"rana",
                "email":"rana@email",
                "phone":"0123456789",
                "language":"English"}
    response = requests.post(user_url, json=user_data)
    status = response.status_code
    user1_resp = response.json()
    self.assertEqual(status,200)
    self.assertEqual(user1_resp["_id"], user_data["user_id"])
    self.assertEqual(user1_resp["name"], user_data["name"])
    self.assertEqual(user1_resp["email"], user_data["email"])
    self.assertEqual(user1_resp["phone"], user_data["phone"])
    self.assertEqual(user1_resp["language"], user_data["language"])

    response = requests.get(f"{user_url}/{user_data['user_id']}")
    status = response.status_code
    user1_resp = response.json()
    self.assertEqual(status, 200)
    self.assertEqual(user1_resp["_id"], user_data["user_id"])
    self.assertEqual(user1_resp["name"], user_data["name"])
    self.assertEqual(user1_resp["email"], user_data["email"])
    self.assertEqual(user1_resp["phone"], user_data["phone"])
    self.assertEqual(user1_resp["language"], user_data["language"])

  @pytest.mark.dependency(name="testb_add_route")
  def testb_add_route(self):
    # Add a new route
    new_route_url = f"{BASE_URL}/route"
    route_data = {"route_id":"test2route",
                  "start_point":"a",
                  "end_point":"e",
                  "stops":["a","b","c","d","e"]}
    response = requests.post(new_route_url, json=route_data)
    status = response.status_code
    route_1_resp = response.json()
    self.assertEqual(status, 200)
    self.assertEqual(route_1_resp["_id"], route_data["route_id"])
    self.assertEqual(route_1_resp["start_point"], route_data["start_point"])
    self.assertEqual(route_1_resp["end_point"], route_data["end_point"])
    self.assertEqual(route_1_resp["stops"], route_data["stops"])

  @pytest.mark.dependency(name="testc_add_ride")
  def testc_add_ride(self):
    # Add a new ride, given a route exists
    route_url = f"{BASE_URL}/route"
    ride_url = f"{BASE_URL}/ride"

    route_data = {"route_id":"test3route",
                "start_point":"b",
                "end_point":"f",
                "stops":["b","c","d","e","f"]}
    route = requests.post(route_url, json=route_data)
    ride_data = {"ride_id":"test3ride",
                "route_id":route_data["route_id"]}
    response = requests.post(ride_url, json=ride_data)
    status = response.status_code
    ride_resp = response.json()
    self.assertEqual(status, 200)

    response = requests.get(f"{ride_url}/{ride_data['ride_id']}")
    ride_resp = response.json()
    self.assertEqual(ride_resp["_id"], ride_data["ride_id"])
    self.assertEqual(ride_resp["route_id"], route_data["route_id"])
    self.assertFalse(ride_resp["ongoing"])
    self.assertFalse(ride_resp["current_stop"])
    self.assertFalse(ride_resp["users"])

  @pytest.mark.dependency(name="testd_add_user_to_ride")
  def testd_add_user_to_ride(self):
    # Add a user to a ride, given the ride and user exists
    user_url = f"{BASE_URL}/user"
    route_url = f"{BASE_URL}/route"
    ride_url = f"{BASE_URL}/ride"
    user_data = {"user_id":"test4user",
                "name":"ahmed",
                "email":"ahmed@email",
                "phone":"0123456789",
                "language":"French"}
    response = requests.post(user_url, json=user_data)
    route_data = {"route_id":"test4route",
                "start_point":"m",
                "end_point":"p",
                "stops":["m","n","o","p"]}
    route = requests.post(route_url, json=route_data)
    ride_data = {"ride_id":"test4ride",
                "route_id":route_data["route_id"]}
    response = requests.post(ride_url, json=ride_data)

    user_to_ride_data = {"ride_id":ride_data["ride_id"],
                        "user_id":user_data["user_id"],
                        "start_point":"m",
                        "end_point":"o"}
    ride_before_resp = requests.get(f"{ride_url}/{ride_data['ride_id']}")
    ride_before = response.json()
    # verify user wasnt added to ride before
    self.assertFalse(any(user["user"]==user_to_ride_data['user_id'] for user in ride_before["users"]))
    # add user to ride
    response = requests.post(f"{ride_url}/add_user", json=user_to_ride_data)
    status = response.status_code
    updated_ride = response.json()
    self.assertEqual(status,200)
    self.assertTrue(any(user["user"]==user_to_ride_data['user_id'] for user in updated_ride["users"]))
    for user in updated_ride["users"]:
      if user["user"]==user_to_ride_data['user_id']:
        self.assertEqual(user["start_point"],user_to_ride_data["start_point"])
        self.assertEqual(user["end_point"],user_to_ride_data["end_point"])
        self.assertFalse(user["onboard"])
        self.assertFalse(user["completed"])

  @pytest.mark.dependency(name="teste_start_ride",depends=["testd_add_user_to_ride"])
  def teste_start_ride(self):
    # Start a ride given it exists
    ride_url = f"{BASE_URL}/ride"
    route_data = {"route_id":"test4route",
                "start_point":"m",
                "end_point":"p",
                "stops":["m","n","o","p"]}
    ride_data = {"ride_id":"test4ride",
                "route_id":route_data["route_id"]}

    ride_before_resp = requests.get(f"{ride_url}/{ride_data['ride_id']}")
    ride_before = ride_before_resp.json()
    self.assertFalse(ride_before["ongoing"])
    # Start ride
    response = requests.post(f"{ride_url}/start/{ride_data['ride_id']}")
    status = response.status_code
    self.assertEqual(status,200)
    updated_ride = response.json()
    self.assertTrue(updated_ride["ongoing"])

  @pytest.mark.dependency(name="testf_onboard_user",depends=["teste_start_ride"])
  def testf_onboard_user(self):
    """
    Make user onboard to a ride, given the ride and user exists and the ride is ongoing
    """
    ride_url = f"{BASE_URL}/ride"
    user_data = {"user_id":"test4user",
                "name":"ahmed",
                "email":"ahmed@email",
                "phone":"0123456789",
                "language":"French"}
    ride_data = {"ride_id":"test4ride"}
    ride_before_resp = requests.get(f"{ride_url}/{ride_data['ride_id']}")
    ride_before = ride_before_resp.json()
    self.assertTrue(any(user["user"]==user_data["user_id"]
               and not user["onboard"]
               for user in ride_before["users"]))
    # for user in ride_before["users"]:
    #   if user["user"]==user_data['user_id']:
    #     self.assertFalse(user["onboard"])

    response = requests.post(f"{ride_url}/user_onboard", json={"ride_id":ride_data['ride_id'],"user_id":user_data['user_id']})
    status = response.status_code
    self.assertEqual(status,200)
    updated_ride = response.json()
    self.assertTrue(any(user["user"]==user_data['user_id']
               and user["onboard"] for user in updated_ride["users"]))

  @pytest.mark.dependency(name="testg_ride_next_stop",depends=["testf_onboard_user"])
  def testg_ride_next_stop(self):
    """
    Move ride to its next stop in its route
    """
    ride_url = f"{BASE_URL}/ride"
    route_data = {"route_id":"test4route",
                "start_point":"m",
                "end_point":"p",
                "stops":["m","n","o","p"]}
    ride_data = {"ride_id":"test4ride",
                "route_id":route_data["route_id"]}
    ride_before_resp = requests.get(f"{ride_url}/{ride_data['ride_id']}")
    ride_before = ride_before_resp.json()
    stop_before = ride_before["current_stop"]

    response = requests.post(f"{ride_url}/next_stop/{ride_data['ride_id']}")
    status = response.status_code
    self.assertEqual(status, 200)
    updated_ride = response.json()
    stop_before_pos = route_data["stops"].index(stop_before)
    curr_pos = route_data["stops"].index(updated_ride["current_stop"])
    self.assertEqual(curr_pos, stop_before_pos + 1)

  @pytest.mark.dependency(name="testh_offboard_user",depends=["testg_ride_next_stop"])
  def testh_offboard_user(self):
    """
    Offboard a user on an ongoing ride given the user is added to the ride and both exist
    """
    ride_url = f"{BASE_URL}/ride"
    user_data = {"user_id":"test4user",
                "name":"ahmed",
                "email":"ahmed@email",
                "phone":"0123456789",
                "language":"French"}
    ride_data = {"ride_id":"test4ride"}
    response = requests.post(f"{ride_url}/next_stop/{ride_data['ride_id']}")

    ride_before_resp = requests.get(f"{ride_url}/{ride_data['ride_id']}")
    ride_before = ride_before_resp.json()
    self.assertTrue(any(user["user"]==user_data['user_id']
               and user["onboard"]
               for user in ride_before["users"]))

    response = requests.post(f"{ride_url}/user_offboard", json={"ride_id":ride_data['ride_id'],"user_id":user_data['user_id']})
    status = response.status_code
    assert status == 200
    updated_ride = response.json()
    self.assertTrue(any(user["user"]==user_data['user_id']
               and not user["onboard"]
               and user["completed"]
               for user in updated_ride["users"]))

  @pytest.mark.dependency(name="testi_group_sms",depends=["testf_onboard_user"])
  def testi_group_sms(self):
    """
    Send a group sms to all users with a promo code for each group grouping them by the language they user
    Get the notifications of a user before and after sending the sms and check it increased
    """
    user_data = {"user_id":"test4user",
                "name":"ahmed",
                "email":"ahmed@email",
                "phone":"0123456789",
                "language":"French"}
    sms_url = f"{BASE_URL}/notifications/sms"

    response = requests.get(f"{sms_url}/{user_data['user_id']}")
    status = response.status_code
    self.assertEqual(status, 200)
    notifications = response.json()
    self.assertEqual(notifications,[])

    response = requests.post(sms_url, json={"sms_type":"group"})
    status = response.status_code
    self.assertEqual(status, 200)

    response = requests.get(f"{sms_url}/{user_data['user_id']}")
    status = response.status_code
    self.assertEqual(status, 200)
    new_notifications = response.json()
    self.assertTrue(len(new_notifications) > len(notifications))

  @pytest.mark.dependency(name="testj_single_sms",depends=["testh_offboard_user"])
  def testj_single_sms(self):
    """
    Send a single sms with a promo code to each user that completed 1 ride
    Get the notifications of a user before and after sending the sms and check it increased
    """
    user_data = {"user_id":"test4user",
                "name":"ahmed",
                "email":"ahmed@email",
                "phone":"0123456789",
                "language":"French"}
    sms_url = f"{BASE_URL}/notifications/sms"

    response = requests.get(f"{sms_url}/{user_data['user_id']}")
    status = response.status_code
    self.assertEqual(status, 200)
    notifications = response.json()

    response = requests.post(sms_url, json={"sms_type":"custom","number_of_rides":1})
    status = response.status_code
    self.assertEqual(status, 200)

    response = requests.get(f"{sms_url}/{user_data['user_id']}")
    status = response.status_code
    self.assertEqual(status, 200)
    new_notifications = response.json()
    self.assertTrue(len(new_notifications) > len(notifications))








