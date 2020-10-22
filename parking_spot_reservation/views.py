import json

from django.http import HttpResponse
from django.views.decorators.http import require_http_methods

from parking_spot_reservation.models import User, ParkingSpots
from parking_spot_reservation.utils import register_user, \
    delete_user, add_parking_spot, delete_parking_spot, \
    EmptyRequestBodyException, InvalidJsonException, \
    InvalidMobileNumberException, InvalidUserException, \
    InvalidParkingException


# Create your views here.


@require_http_methods(['POST', 'DELETE'])
def register(request):
    if request.method == 'POST':
        try:
            result = register_user(request)
            if result:
                return HttpResponse("Registration Success")
            else:
                return HttpResponse("Something went wrong", status=500)
        except EmptyRequestBodyException:
            return HttpResponse("No parameters found in request body", status=400)
        except InvalidJsonException:
            return HttpResponse("Invalid Json in Request body", status=400)
        except InvalidMobileNumberException:
            return HttpResponse("Invalid Mobile Number", status=400)
        except InvalidUserException:
            return HttpResponse("User with this mobile number already exists", status=400)

    elif request.method == 'DELETE':
        try:
            result = delete_user(request)
            if result:
                return HttpResponse("User deleted successfully")
            else:
                return HttpResponse("Something went wrong", status=500)
        except EmptyRequestBodyException:
            return HttpResponse("No parameters found in request body", status=400)
        except InvalidJsonException:
            return HttpResponse("Invalid Json in Request body", status=400)
        except InvalidUserException:
            return HttpResponse("User does not exist", status=400)


@require_http_methods(['GET'])
def all_users(request):
    users = User.objects.all()
    users_dict = {}
    users_list = []
    for user in users.iterator():
        user_dict = dict()
        user_dict['mobile_number'] = user.mobile_number
        user_dict['email_id'] = user.email_id
        users_list.append(user_dict)

    users_dict['users'] = users_list

    response_json = json.dumps(users_dict, indent=4)
    return HttpResponse(response_json, content_type='application/json')


@require_http_methods(['POST', 'DELETE'])
def parking_spot(request):
    if request.method == 'POST':
        try:
            result = add_parking_spot(request)
            if result:
                return HttpResponse("Parking spot added successfully")
            else:
                return HttpResponse("Something went wrong", status=500)
        except EmptyRequestBodyException:
            return HttpResponse("No parameters found in request body", status=400)
        except InvalidJsonException:
            return HttpResponse("Invalid Json in Request body", status=400)
        except InvalidParkingException:
            return HttpResponse("Parking spot already exists", status=400)

    elif request.method == 'DELETE':
        try:
            result = delete_parking_spot(request)
            if result:
                return HttpResponse("Parking spot deleted successfully")
            else:
                return HttpResponse("Something went wrong", status=500)
        except EmptyRequestBodyException:
            return HttpResponse("No parameters found in request body", status=400)
        except InvalidJsonException:
            return HttpResponse("Invalid Json in Request body", status=400)
        except InvalidParkingException:
            return HttpResponse("Parking spot does not exists", status=400)


@require_http_methods(['GET'])
def available_parking_spots(request):
    sections = {1: "SECTION_A", 2: "SECTION_B", 3: "SECTION_AB"}
    spots = ParkingSpots.objects.exclude(availability=0)
    spots_dict = {}
    spots_list = []
    for spot in spots.iterator():
        spot_dict = dict()
        spot_dict['latitude'] = spot.latitude
        spot_dict['longitude'] = spot.longitude
        spot_dict['cost_per_hour'] = spot.cost_per_hour
        spot_dict['currency'] = spot.currency
        spot_dict['availability'] = sections[spot.availability]

        spots_list.append(spot_dict)

    spots_dict['available_parking_spots'] = spots_list

    response_json = json.dumps(spots_dict, indent=4)
    return HttpResponse(response_json, content_type='application/json')
