from django.urls import path

from parking_spot_reservation import views

urlpatterns = [
    path('register', views.register, name='register'),
    path('all_users', views.all_users, name='all_users'),
    path('parking_spot', views.parking_spot, name='parking_spot'),
    path('available_parking_spots', views.available_parking_spots, name='available_parking_spots'),
    path('nearby_spots', views.nearby_spots, name='nearby_spots'),
    path('reserve_parking', views.reserve_parking, name='reserve_parking'),
    path('reservations', views.reservations, name='reservations'),
    path('reservation_cost', views.reservation_cost, name='reservation_cost'),
]
