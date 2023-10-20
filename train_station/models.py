from django.db import models

from train_station_service import settings


class Station(models.Model):
    name = models.CharField(max_length=31, unique=True)
    latitude = models.FloatField()
    longitude = models.FloatField()

    def __str__(self):
        return self.name


class Crew(models.Model):
    first_name = models.CharField(max_length=31)
    last_name = models.CharField(max_length=31)

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
    distance = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.source} -> {self.destination}"


class Train(models.Model):
    name = models.CharField(max_length=31)
    cargo_number = models.PositiveIntegerField()
    places_in_cargo = models.PositiveIntegerField()
    train_type = models.ForeignKey(
        TrainType, on_delete=models.CASCADE, related_name="trains"
    )

    def __str__(self):
        return self.name


class Order(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    # user = models.ForeignKey(
    #     to=settings.AUTH_USER_MODEL,
    #     on_delete=models.CASCADE,
    #     related_name="orders",
    # )


class Journey(models.Model):
    route = models.ForeignKey(
        to=Route, on_delete=models.CASCADE, related_name="journeys"
    )
    train = models.ForeignKey(
        to=Train, on_delete=models.CASCADE, related_name="journeys"
    )
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()

    def __str__(self):
        return f"{self.route}: {self.train}"


class Ticket(models.Model):
    cargo = models.PositiveIntegerField()
    seat = models.PositiveIntegerField()
    journey = models.ForeignKey(
        to=Route, on_delete=models.CASCADE, related_name="tickets"
    )
    order = models.ForeignKey(
        to=Order, on_delete=models.CASCADE, related_name="tickets"
    )
