from django.contrib import admin
from parking_spot_reservation.models import User, ParkingSpots, Reservations

# Register your models here.
admin.site.register(User)
admin.site.register(ParkingSpots)
admin.site.register(Reservations)
