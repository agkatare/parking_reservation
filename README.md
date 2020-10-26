# ParkingReservation
Parking Spot Reservation System
## Description: 
This system is build to manage parking spot reservation service. User can search for nearby parking spot
using (latitude and longitude) and radius; and can reserve the parking spot. This system manages parking
for 2-wheeler and 4-wheeler vehicles. In this we consider every parking spot is for 4-wheeler and by dividing
it into 2 sections we can use it for two 2-wheelers.
For Example:
There is one parking spot at location (10.0, 10.5) [latitude,longitude]. So on this parking spot we can park
4-wheeler in complete area (say SECTION_AB) or we can park two 2-wheelers (one in SECTION_A and other in
SECTION_B).
User can cancel the reservation if required. There is an option to mark reservation spot as parked by checking-in 
api and to free the reservation spot by check-out api. Based on the reservation time we calculate the amount 
user has been charged for parking. Admin can view all the existing reservations in the system.

## API's list:
	1. register: User can register himself/herselg using mobile number
	2. all_users: Admin can view all the registered users
	3. parking_spot: Admin can add or delete the parking spot
	4. available_parking_spots: User can view all the available parking spots
	5. nearby_spots: User can search for nearby parking spots by providing location (latitude, longitude) and radius
	6. reserve_parking: User can reserve the parking
	7. reservations: Admin can view all the reservations.
	8. reservation_cost: User can search for the cost for existing reservation or the reservation to be made.
    
##  Tech stack
### Python
### Django
### Json
### sqlite
 
