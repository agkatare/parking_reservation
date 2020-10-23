import re
import hashlib
import json
import uuid
import math
from json import JSONDecodeError
from datetime import datetime

from parking_spot_reservation.models import User, ParkingSpots, Reservations

sections = {0: "RESERVED", 1: "SECTION_A", 2: "SECTION_B", 3: "SECTION_AB"}
sections_keys = {"RESERVED": 0, "SECTION_A": 1, "SECTION_B": 2, "SECTION_AB": 3}
reserve_type = {"ALLOCATE": 0, "DE-ALLOCATE": 1}
status = {1: "RESERVED", 2: "PARKED", 3: "COMPLETED", 4: "CANCELLED"}
parking_status = {"RESERVED": 1, "PARKED": 2, "COMPLETED": 3, "CANCELLED": 4}


class InvalidParkingException(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


class InvalidRequestBodyException(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


class InvalidJsonException(Exception):
    pass


class InvalidMobileNumberException(Exception):
    pass


class InvalidUserException(Exception):
    pass


class InvalidReservationException(Exception):
    pass


def validate_mobile_number(number):
    pattern = re.compile("(0/91)?[7-9][0-9]{9}")
    return pattern.match(number)


def register_user(request):
    result = False
    body_unicode = request.body.decode('utf-8')
    if body_unicode == "":
        raise InvalidRequestBodyException("No parameters found in request body")

    try:
        body = json.loads(body_unicode)
    except JSONDecodeError as je:
        raise InvalidJsonException

    mobile_number = body['mobile_number']
    email_id = body['email_id']
    password = body['password']

    if not validate_mobile_number(mobile_number):
        raise InvalidMobileNumberException

    pass_hash = hashlib.sha256((email_id + password).encode())

    try:
        user = User.objects.get(mobile_number=mobile_number)
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
        raise InvalidRequestBodyException("No parameters found in request body")

    try:
        body = json.loads(body_unicode)
    except Exception:
        raise InvalidJsonException

    mobile_number = body['mobile_number']
    try:
        user = User.objects.get(mobile_number=mobile_number)
        user.delete()
        result = True
        return result
    except User.DoesNotExist:
        raise InvalidUserException


def add_parking_spot(request):
    result = False
    body_unicode = request.body.decode('utf-8')
    if body_unicode == "":
        raise InvalidRequestBodyException("No parameters found in request body")

    try:
        body = json.loads(body_unicode)
    except JSONDecodeError as je:
        raise InvalidJsonException

    latitude = body['latitude']
    longitude = body['longitude']
    cost = body['cost_per_hour']
    currency = body['currency']

    try:
        spot = ParkingSpots.objects.get(latitude=latitude, longitude=longitude)
        raise InvalidParkingException
    except ParkingSpots.DoesNotExist:
        query = ParkingSpots(uuid.uuid1(), latitude, longitude, cost, currency, 3)
        query.save()
        result = True
        return result


def delete_parking_spot(request):
    result = False
    body_unicode = request.body.decode('utf-8')
    if body_unicode == "":
        raise InvalidRequestBodyException("No parameters found in request body")

    try:
        body = json.loads(body_unicode)
    except JSONDecodeError as je:
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


def get_all_parking_spots():
    spots = ParkingSpots.objects.all()
    spots_dict = {}
    spots_list = []
    for spot in spots.iterator():
        spot_dict = dict()
        spot_dict['spot_id'] = str(spot.spot_id)
        spot_dict['latitude'] = spot.latitude
        spot_dict['longitude'] = spot.longitude
        spot_dict['cost_per_hour'] = spot.cost_per_hour
        spot_dict['currency'] = spot.currency
        spot_dict['availability'] = sections[spot.availability]

        spots_list.append(spot_dict)

    spots_dict['available_parking_spots'] = spots_list
    return spots_dict


def search_spots(request):
    body_unicode = request.body.decode('utf-8')
    if body_unicode == "":
        raise InvalidRequestBodyException("No parameters found in request body")

    try:
        body = json.loads(body_unicode)
    except JSONDecodeError as je:
        raise InvalidJsonException

    if 'latitude' not in body or 'longitude' not in body or 'radius' not in body:
        raise InvalidRequestBodyException(
            "Latitude/Longitude/Radius not found in request body")

    latitude = body['latitude']
    longitude = body['longitude']
    radius = body['radius']

    source_point = (longitude, latitude)
    all_spots = get_all_parking_spots()
    spots = all_spots['available_parking_spots']
    filtered_spots_list = []
    for spot in spots:
        location = (spot['longitude'], spot['latitude'])
        distance = math.sqrt(abs(sum([(a - b) for a, b in zip(source_point, location)])))
        if distance <= radius:
            filtered_spots_list.append(spot)

    nearby_spots_dict = {'nearby_spots': filtered_spots_list}
    return nearby_spots_dict


def validate_spot(vehicle_type, latitude, longitude, section, start_time, end_time):
    if vehicle_type.lower() == '2-wheeler':
        if section == 'RESERVED' or section == 'SECTION_AB':
            return False, None

    if vehicle_type.lower() == '4-wheeler':
        if section == 'RESERVED' or section == 'SECTION_A' or section == 'SECTION_B':
            return False, None
    try:
        spot = ParkingSpots.objects.get(latitude=latitude, longitude=longitude)
        if vehicle_type.lower() == '2-wheeler':
            if spot.availability == sections_keys[section] \
                    or spot.availability == sections_keys['SECTION_AB']:
                pass
            else:
                return False, None

        if vehicle_type.lower() == '4-wheeler':
            if spot.availability != sections_keys['SECTION_AB']:
                return False, None

        reservations = Reservations.objects.filter(spot=spot,
                                                   status=parking_status['RESERVED'],
                                                   section=sections_keys[section])
        for reserved in reservations.iterator():
            if (start_time.replace(tzinfo=None) < reserved.start_time.replace(tzinfo=None)
                and end_time.replace(tzinfo=None) < reserved.start_time.replace(tzinfo=None)) \
                    or (start_time.replace(tzinfo=None) > reserved.end_time.replace(tzinfo=None)
                        and end_time.replace(tzinfo=None) > reserved.end_time.replace(tzinfo=None)):
                return False, None

        reservations = Reservations.objects.filter(spot=spot,
                                                   status=parking_status['PARKED'],
                                                   section=sections_keys[section])
        for reserved in reservations.iterator():
            if (start_time.replace(tzinfo=None) < reserved.start_time.replace(tzinfo=None)
                and end_time.replace(tzinfo=None) < reserved.start_time.replace(tzinfo=None)) \
                    or (start_time.replace(tzinfo=None) > reserved.end_time.replace(tzinfo=None)
                        and end_time.replace(tzinfo=None) > reserved.end_time.replace(tzinfo=None)):
                return False, None

        return True, spot
    except ParkingSpots.DoesNotExist:
        raise InvalidParkingException()
    except Reservations.DoesNotExist:
        return True, spot


def update_spot_availability(spot_id, section, res_type):
    spot = ParkingSpots.objects.get(spot_id=spot_id)
    if section == sections[sections_keys['SECTION_AB']]:
        if res_type == reserve_type['ALLOCATE']:
            if spot.availability == sections_keys['SECTION_AB']:
                spot.availability = sections_keys['RESERVED']
        if res_type == reserve_type['DE-ALLOCATE']:
            if spot.availability == sections_keys['RESERVED']:
                spot.availability = sections_keys['SECTION_AB']

    if section == sections[sections_keys['SECTION_A']]:
        if res_type == reserve_type['ALLOCATE']:
            if spot.availability == sections_keys['SECTION_AB']:
                spot.availability = sections_keys['SECTION_B']
            elif spot.availability == sections_keys['SECTION_A']:
                spot.availability = sections_keys['RESERVED']

    if section == sections[sections_keys['SECTION_B']]:
        if res_type == reserve_type['ALLOCATE']:
            if spot.availability == sections_keys['SECTION_AB']:
                spot.availability = sections_keys['SECTION_A']
            elif spot.availability == sections_keys['SECTION_B']:
                spot.availability = sections_keys['RESERVED']

    if section == sections[sections_keys['SECTION_A']]:
        if res_type == reserve_type['DE-ALLOCATE']:
            if spot.availability == sections_keys['RESERVED']:
                spot.availability = sections_keys['SECTION_A']
            elif spot.availability == sections_keys['SECTION_B']:
                spot.availability = sections_keys['SECTION_AB']

    if section == sections[sections_keys['SECTION_B']]:
        if res_type == reserve_type['DE-ALLOCATE']:
            if spot.availability == sections_keys['RESERVED']:
                spot.availability = sections_keys['SECTION_B']
            elif spot.availability == sections_keys['SECTION_A']:
                spot.availability = sections_keys['SECTION_AB']

    spot.save()
    return True


def calculate_bill_amount(spot, start_time, end_time):
    time_diff = abs(end_time.replace(tzinfo=None) - start_time.replace(tzinfo=None))
    total_time_in_hrs = (time_diff.total_seconds() / 3600)
    bill_amount = spot.cost_per_hour * total_time_in_hrs
    return round(bill_amount, 2)


def reserve_parking_spot(request):
    body_unicode = request.body.decode('utf-8')
    if body_unicode == "":
        raise InvalidRequestBodyException("No parameters found in request body")

    try:
        body = json.loads(body_unicode)
    except JSONDecodeError as je:
        raise InvalidJsonException

    if 'user_id' not in body or 'vehicle_type' not in body \
            or 'latitude' not in body or 'longitude' not in body \
            or 'section' not in body or 'start_time' not in body \
            or 'end_time' not in body or 'vehicle_number' not in body:
        raise InvalidRequestBodyException("Missing parameters in request body")

    user_id = body['user_id']
    vehicle_type = body['vehicle_type']
    vehicle_number = body['vehicle_number']
    latitude = body['latitude']
    longitude = body['longitude']
    section = body['section']
    start = body['start_time']
    end = body['end_time']
    start_time = datetime.strptime(start, "%Y-%m-%d %H:%M:%S")
    end_time = datetime.strptime(end, "%Y-%m-%d %H:%M:%S")

    if (start_time.replace(tzinfo=None) < datetime.now().replace(tzinfo=None)
        or end_time.replace(tzinfo=None) < datetime.now().replace(tzinfo=None)) \
            and start_time < end_time:
        raise InvalidRequestBodyException("Invalid start_time or end_time")

    try:
        user = User.objects.get(mobile_number=user_id)
    except User.DoesNotExist:
        raise InvalidUserException

    ret, spot = validate_spot(vehicle_type, latitude, longitude, section, start_time, end_time)
    if not ret:
        raise InvalidParkingException("Invalid Parking spot selected")

    ret = update_spot_availability(spot.spot_id, section, reserve_type['ALLOCATE'])
    if not ret:
        raise InvalidParkingException("Parking spot availability update failed")

    bill_amount = calculate_bill_amount(spot, start_time, end_time)
    query = Reservations(reservation_id=uuid.uuid1(), user=user, spot=spot,
                         vehicle_number=vehicle_number, section=sections_keys[section],
                         start_time=start_time, end_time=end_time,
                         status=parking_status['RESERVED'], bill_amount=bill_amount)
    query.save()
    return True


def cancel_reservation(request):
    body_unicode = request.body.decode('utf-8')
    if body_unicode == "":
        raise InvalidRequestBodyException("No parameters found in request body")

    try:
        body = json.loads(body_unicode)
    except JSONDecodeError as je:
        raise InvalidJsonException

    if 'user_id' not in body or 'latitude' not in body \
            or 'longitude' not in body or 'section' not in body:
        raise InvalidRequestBodyException("Missing parameters in request body")

    user_id = body['user_id']
    latitude = body['latitude']
    longitude = body['longitude']
    section = body['section']
    end_time = datetime.now()

    try:
        user = User.objects.get(mobile_number=user_id)
        spot = ParkingSpots.objects.get(latitude=latitude, longitude=longitude)
    except User.DoesNotExist:
        raise InvalidUserException
    except ParkingSpots.DoesNotExist:
        raise InvalidParkingException("Parking spot does not exist")
    try:
        reservation = Reservations.objects.get(spot=spot, user=user,
                                               section=sections_keys[section],
                                               status=parking_status['RESERVED'])
    except Reservations.DoesNotExist:
        try:
            reservation = Reservations.objects.get(spot=spot, user=user,
                                                   section=sections_keys[section],
                                                   status=parking_status['PARKED'])
        except Reservations.DoesNotExist:
            raise InvalidReservationException

    bill_amount = calculate_bill_amount(spot, reservation.start_time, end_time)
    reservation.end_time = end_time
    reservation.bill_amount = bill_amount
    reservation.status = parking_status['CANCELLED']

    ret = update_spot_availability(spot.spot_id, section, reserve_type['DE-ALLOCATE'])
    if not ret:
        raise InvalidParkingException("Parking spot availability update failed")
    reservation.save()
    return True


def get_all_reservations():
    reservations = Reservations.objects.all()
    reservations_dict = {}
    reservations_list = []
    for res in reservations.iterator():
        res_dict = dict()
        res_dict['reservation_id'] = str(res.reservation_id)
        res_dict['user_id'] = res.user.mobile_number
        res_dict['spot_id'] = str(res.spot.spot_id)
        res_dict['vehicle_number'] = res.vehicle_number
        res_dict['section'] = sections[res.section]
        res_dict['start_time'] = str(res.start_time)
        res_dict['end_time'] = str(res.end_time)
        res_dict['status'] = status[res.status]
        res_dict['bill_amount'] = res.bill_amount

        reservations_list.append(res_dict)

    reservations_dict['reservations'] = reservations_list
    return reservations_dict


def get_reservation_cost(request):
    body_unicode = request.body.decode('utf-8')
    if body_unicode == "":
        raise InvalidRequestBodyException("No parameters found in request body")

    try:
        body = json.loads(body_unicode)
    except JSONDecodeError as je:
        raise InvalidJsonException

    if 'reservation_id' not in body:
        if 'latitude' not in body or 'longitude' not in body \
                or 'start_time' not in body or 'end_time' not in body \
                or 'section' not in body:
            raise InvalidRequestBodyException("Missing parameters in request body")

    if 'reservation_id' in body:
        r_id = body['reservation_id']
        reserve_id = uuid.UUID(r_id)
        reservation = Reservations.objects.get(reservation_id=reserve_id)
        cost = reservation.bill_amount
    else:
        latitude = body['latitude']
        longitude = body['longitude']
        start = body['start_time']
        end = body['end_time']
        start_time = datetime.strptime(start, "%Y-%m-%d %H:%M:%S")
        end_time = datetime.strptime(end, "%Y-%m-%d %H:%M:%S")

        spot = ParkingSpots.objects.get(latitude=latitude, longitude=longitude)
        cost = calculate_bill_amount(spot, start_time, end_time)

    return cost


def update_reservation(request, operation):
    body_unicode = request.body.decode('utf-8')
    if body_unicode == "":
        raise InvalidRequestBodyException("No parameters found in request body")

    try:
        body = json.loads(body_unicode)
    except JSONDecodeError as je:
        raise InvalidJsonException

    if 'reservation_id' not in body:
        raise InvalidRequestBodyException("Missing parameters in request body")

    r_id = body['reservation_id']
    reserve_id = uuid.UUID(r_id)
    reservation = Reservations.objects.get(reservation_id=reserve_id)

    if operation.lower() == 'check-in':
        reservation.status = parking_status['PARKED']

    elif operation.lower() == 'check-out':
        end_time = datetime.now()
        ret = update_spot_availability(reservation.spot.spot_id,
                                       sections[reservation.section],
                                       reserve_type['DE-ALLOCATE'])
        if not ret:
            raise InvalidParkingException("Parking spot availability update failed")

        cost = calculate_bill_amount(reservation.spot, reservation.start_time, end_time)
        reservation.status = parking_status['COMPLETED']
        reservation.end_time = end_time
        reservation.bill_amount = cost

    reservation.save()
    return True
