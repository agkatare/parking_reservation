from django.db import models


# Create your models here.

class User(models.Model):
    mobile_number = models.CharField(max_length=12, primary_key=True)
    email_id = models.EmailField()
    password = models.TextField()


class ParkingSpots(models.Model):
    class Sections(models.IntegerChoices):
        RESERVED = 0
        SECTION_A = 1
        SECTION_B = 2
        SECTION_AB = 3
    spot_id = models.UUIDField(primary_key=True)
    latitude = models.FloatField()
    longitude = models.FloatField()
    cost_per_hour = models.IntegerField()
    currency = models.CharField(max_length=5)
    availability = models.IntegerField(choices=Sections.choices)


class Reservations(models.Model):
    class Sections(models.IntegerChoices):
        SECTION_A = 1
        SECTION_B = 2
        SECTION_AB = 3

    class Status(models.IntegerChoices):
        RESERVED = 1
        PARKED = 2
        COMPLETED = 3
        CANCELLED = 4
    reservation_id = models.UUIDField()
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    spot = models.ForeignKey(ParkingSpots, on_delete=models.RESTRICT)
    section = models.IntegerField(choices=Sections.choices)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    status = models.IntegerField(choices=Status.choices)
    bill_amount = models.IntegerField()


class UserLogin(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.TextField()
