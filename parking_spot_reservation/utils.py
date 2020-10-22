import re
import hashlib
import json
import uuid
from json import JSONDecodeError

from parking_spot_reservation.models import User, ParkingSpots


class InvalidParkingException(Exception):
    pass


class EmptyRequestBodyException(Exception):
    pass


class InvalidJsonException(Exception):
    pass


class InvalidMobileNumberException(Exception):
    pass


class InvalidUserException(Exception):
    pass


def validate_mobile_number(number):
    pattern = re.compile("(0/91)?[7-9][0-9]{9}")
    return pattern.match(number)


def register_user(request):
    result = False
    body_unicode = request.body.decode('utf-8')
    if body_unicode == "":
        raise EmptyRequestBodyException

    try:
        body = json.loads(body_unicode)
    except JSONDecodeError as je:
        print("Invalid json in request body")
        raise InvalidJsonException

    mobile_number = body['mobile_number']
    email_id = body['email_id']
    password = body['password']

    if not validate_mobile_number(mobile_number):
        raise InvalidMobileNumberException

    pass_hash = hashlib.sha256((email_id + password).encode())

    try:
        user = User.objects.get(mobile_number=mobile_number)
        print("User with this mobile number already exists")
        raise InvalidUserException
    except User.DoesNotExist:
        query = User(mobile_number, email_id, pass_hash)
        query.save()
        result = True
        return result


def delete_user(request):
    result = False
    body_unicode = request.body.decode('utf-8')

    if body_unicode == "":
        raise EmptyRequestBodyException

    try:
        body = json.loads(body_unicode)
    except Exception:
        print("Invalid json in request body")
        raise InvalidJsonException

    mobile_number = body['mobile_number']
    try:
        user = User.objects.get(mobile_number=mobile_number)
        user.delete()
        result = True
        return result
    except User.DoesNotExist:
        print("User does not exist")
        raise InvalidUserException


def add_parking_spot(request):
    result = False
    body_unicode = request.body.decode('utf-8')
    if body_unicode == "":
        raise EmptyRequestBodyException

    try:
        body = json.loads(body_unicode)
    except JSONDecodeError as je:
        print("Invalid json in request body")
        raise InvalidJsonException

    latitude = body['latitude']
    longitude = body['longitude']
    cost = body['cost_per_hour']
    currency = body['currency']

    try:
        spot = ParkingSpots.objects.get(latitude=latitude, longitude=longitude)
        print("Parking spot already exist")
        raise InvalidParkingException
    except ParkingSpots.DoesNotExist:
        query = ParkingSpots(uuid.uuid1(), latitude, longitude, cost, currency, 0)
        query.save()
        result = True
        return result


def delete_parking_spot(request):
    result = False
    body_unicode = request.body.decode('utf-8')
    if body_unicode == "":
        raise EmptyRequestBodyException

    try:
        body = json.loads(body_unicode)
    except JSONDecodeError as je:
        print("Invalid json in request body")
        raise InvalidJsonException

    latitude = body['latitude']
    longitude = body['longitude']

    try:
        spot = ParkingSpots.objects.get(latitude=latitude, longitude=longitude)
        spot.delete()
        result = True
        return result
    except ParkingSpots.DoesNotExist:
        print("Parking spot does not exist")
        raise InvalidParkingException
