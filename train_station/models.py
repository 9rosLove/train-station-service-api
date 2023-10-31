import os
import uuid

from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils import timezone
from django.utils.text import slugify
from geopy.distance import geodesic

from train_station_service import settings


class Address(models.Model):
    country = models.CharField(max_length=31, null=True)
    city = models.CharField(max_length=31, null=True)

    def __str__(self):
        address_components = [self.country, self.city]
        address_string = ", ".join(filter(None, address_components))
        if address_string:
            return address_string
        return "Unknown address"


def station_image_file_path(instance, filename):
    _, extension = os.path.splitext(filename)
    filename = f"{slugify(instance.name)}-{uuid.uuid4()}{extension}"

    return os.path.join("uploads/stations/", filename)


class Station(models.Model):
    name = models.CharField(max_length=31, unique=True)
    latitude = models.DecimalField(
        max_digits=11,
        decimal_places=9,
        validators=[
            MinValueValidator(-90.0, message="Latitude must be at least -90."),
            MaxValueValidator(90.0, message="Latitude must be at most 90."),
        ],
    )
    longitude = models.DecimalField(
        max_digits=12,
        decimal_places=9,
        validators=[
            MinValueValidator(
                -180.0, message="Longitude must be at least -180."
            ),
            MaxValueValidator(180.0, message="Longitude must be at most 180."),
        ],
    )
    address = models.ForeignKey(
        to=Address,
        on_delete=models.CASCADE,
    )

    image = models.ImageField(upload_to=station_image_file_path, null=True)

    class Meta:
        unique_together = ("name", "latitude", "longitude")

    def __str__(self):
        return self.name


class Crew(models.Model):
    first_name = models.CharField(max_length=31)
    last_name = models.CharField(max_length=31)

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class TrainType(models.Model):
    name = models.CharField(max_length=31, unique=True)

    def __str__(self):
        return self.name


class Route(models.Model):
    source = models.ForeignKey(
        Station, on_delete=models.CASCADE, related_name="source_routes"
    )
    destination = models.ForeignKey(
        Station, on_delete=models.CASCADE, related_name="destination_routes"
    )

    @property
    def distance_in_kilometers(self):
        source = (self.source.latitude, self.source.longitude)
        destination = (self.destination.latitude, self.destination.longitude)
        distance = int(geodesic(source, destination).kilometers)

        return distance

    @staticmethod
    def validate_station(source, destination, error_to_raise):
        if source == destination:
            raise error_to_raise(
                {"source": "Source and destination should be different."}
            )

    def clean(self):
        Route.validate_station(self.source, self.destination, ValidationError)

    class Meta:
        unique_together = ("source", "destination")

    def __str__(self):
        return f"{self.source} -> {self.destination}"


class Train(models.Model):
    name = models.CharField(max_length=31, unique=True)
    cargo_number = models.PositiveIntegerField()
    places_in_cargo = models.PositiveIntegerField()
    train_type = models.ForeignKey(
        TrainType, on_delete=models.CASCADE, related_name="trains"
    )

    @staticmethod
    def validate_name(name, error_to_raise):
        if len(name) != 8:
            raise error_to_raise({"name": "Name should be 8 characters long."})
        if not name[:3].isalpha() and not name[:3].isupper():
            raise error_to_raise(
                {
                    "name": "First 3 characters should be uppercase Latin letters."
                }
            )
        if not name[3:].isnumeric():
            raise error_to_raise(
                {"name": "Last 5 characters should be numbers."}
            )

    def clean(self):
        Train.validate_name(self.name, ValidationError)

    @property
    def capacity(self):
        return self.places_in_cargo * self.cargo_number

    def __str__(self):
        return self.name


class Order(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(
        to=settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="orders",
    )

    def __str__(self):
        return f"{self.user}: {self.created_at}"


class Journey(models.Model):
    route = models.ForeignKey(
        to=Route, on_delete=models.CASCADE, related_name="journeys"
    )
    train = models.ForeignKey(
        to=Train, on_delete=models.CASCADE, related_name="journeys"
    )
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()
    crew = models.ManyToManyField(to=Crew, related_name="journeys")

    @staticmethod
    def validate_time(departure_time, arrival_time, error_to_raise):
        if departure_time >= arrival_time or departure_time <= timezone.now():
            raise error_to_raise(
                {
                    "departure_time": f"Departure time should be before arrival time and in the future."
                }
            )

    @staticmethod
    def validate_train(train, departure_time, arrival_time, error_to_raise):
        train_journeys = Journey.objects.filter(
            train=train,
            departure_time__lte=arrival_time,
            arrival_time__gte=departure_time,
        )
        if train_journeys.exists():
            raise error_to_raise(
                {"train": f"Train {train} is already on this route."}
            )

    def clean(self):
        Journey.validate_time(
            self.departure_time, self.arrival_time, ValidationError
        )
        Journey.validate_train(
            self.train, self.departure_time, self.arrival_time, ValidationError
        )

    def __str__(self):
        return f"{self.route}: {self.train}"


class Ticket(models.Model):
    cargo = models.PositiveIntegerField()
    seat = models.PositiveIntegerField()
    journey = models.ForeignKey(
        to=Journey, on_delete=models.CASCADE, related_name="tickets"
    )
    order = models.ForeignKey(
        to=Order, on_delete=models.CASCADE, related_name="tickets"
    )

    @staticmethod
    def validate_seat(seat, seats_in_cargo, error_to_raise):
        if not (1 <= seat <= seats_in_cargo):
            raise error_to_raise(
                {
                    "seat": f"Seat number should be in range 1 to {seats_in_cargo}"
                }
            )

    @staticmethod
    def validate_cargo(cargo, cargo_number, error_to_raise):
        if not (1 <= cargo <= cargo_number):
            raise error_to_raise(
                {
                    "cargo": f"Cargo number should be in range 1 to {cargo_number}"
                }
            )

    def clean(self):
        Ticket.validate_seat(
            self.seat, self.journey.train.places_in_cargo, ValidationError
        )
        Ticket.validate_cargo(
            self.cargo, self.journey.train.cargo_number, ValidationError
        )

    class Meta:
        unique_together = ("cargo", "seat", "journey")
