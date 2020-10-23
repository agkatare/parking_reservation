import json
from json import JSONDecodeError

from django.http import HttpResponse
from django.views.decorators.http import require_http_methods

from parking_spot_reservation.models import User
from parking_spot_reservation.utils import register_user, \
    delete_user, add_parking_spot, delete_parking_spot, \
    InvalidRequestBodyException, InvalidJsonException, \
    InvalidMobileNumberException, InvalidUserException, \
    InvalidParkingException, search_spots, get_all_parking_spots, \
    reserve_parking_spot, cancel_reservation, InvalidReservationException, \
    get_all_reservations, get_reservation_cost, update_reservation


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
        except InvalidRequestBodyException as ire:
            return HttpResponse(ire.message, status=400)
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
        except InvalidRequestBodyException as ire:
            return HttpResponse(ire.message, status=400)
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
        except InvalidRequestBodyException as ire:
            return HttpResponse(ire.message, status=400)
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
        except InvalidRequestBodyException as ire:
            return HttpResponse(ire.message, status=400)
        except InvalidJsonException:
            return HttpResponse("Invalid Json in Request body", status=400)
        except InvalidParkingException:
            return HttpResponse("Parking spot does not exists", status=400)


@require_http_methods(['GET'])
def available_parking_spots(request):
    spots_dict = get_all_parking_spots()
    response_json = json.dumps(spots_dict, indent=4)
    return HttpResponse(response_json, content_type='application/json')


@require_http_methods(['GET'])
def nearby_spots(request):
    try:
        parking_spots = search_spots(request)
        response_json = json.dumps(parking_spots, indent=4)
        return HttpResponse(response_json, content_type='application/json')
    except InvalidRequestBodyException as ire:
        return HttpResponse(ire.message, status=400)
    except InvalidJsonException:
        return HttpResponse("Invalid Json in Request body", status=400)


@require_http_methods(['POST'])
def reserve_parking(request):

    operations_set = set(('reserve', 'cancel', 'check-in', 'check-out'))
    if 'operation' not in request.headers:
        return HttpResponse("Operation to perform (Reserve/Cancel/Check-in/Check-out) "
                            "parking spot not found in request headers", status=400)

    operation = request.headers['operation']
    if operation.lower() in operations_set:
        if operation.lower() == 'reserve':
            try:
                result = reserve_parking_spot(request)
                if result:
                    return HttpResponse("Parking spot reservation success")
            except InvalidRequestBodyException as ire:
                return HttpResponse(ire.message, status=400)
            except InvalidJsonException:
                return HttpResponse("Invalid Json in Request body")
            except InvalidParkingException as ipe:
                return HttpResponse(ipe.message, status=400)
        elif operation.lower() == 'cancel':
            try:
                result = cancel_reservation(request)
                if result:
                    return HttpResponse("Parking reservation cancelled")
            except InvalidRequestBodyException as ire:
                return HttpResponse(ire.message, status=400)
            except InvalidJsonException:
                return HttpResponse("Invalid Json in Request body")
            except InvalidUserException:
                return HttpResponse("Invalid user")
            except InvalidParkingException as ipe:
                return HttpResponse(ipe.message, status=400)
            except InvalidReservationException:
                return HttpResponse("Invalid parking reservation", status=400)
        elif operation.lower() == 'check-in' or operation.lower() == 'check-out':
            try:
                result = update_reservation(request, operation)
                if result:
                    return HttpResponse("Success")
            except InvalidRequestBodyException as ire:
                return HttpResponse(ire.message, status=400)
            except InvalidJsonException:
                return HttpResponse("Invalid Json in Request body")
            except InvalidParkingException as ipe:
                return HttpResponse(ipe.message, status=400)
    else:
        return HttpResponse("Invalid operation provided. "
                            "Valid values (Reserve/Cancel)", status=400)


@require_http_methods(['GET'])
def reservations(request):
    reservations_dict = get_all_reservations()
    response_json = json.dumps(reservations_dict, indent=4)
    return HttpResponse(response_json, content_type='application/json')


@require_http_methods(['GET'])
def reservation_cost(request):
    try:
        cost = get_reservation_cost(request)
        amount = {'parking_cost': cost}
        response_json = json.dumps(amount, indent=4)
        return HttpResponse(response_json, content_type='application/json')
    except InvalidRequestBodyException as ire:
        return HttpResponse(ire.message, status=400)
    except InvalidJsonException:
        return HttpResponse("Invalid Json in Request body")
