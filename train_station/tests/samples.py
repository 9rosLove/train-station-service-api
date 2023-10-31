from django.urls import reverse

from train_station.models import (
    TrainType,
    Crew,
    Station,
    Address,
    Route,
)

CREW_URL = reverse("train_station:crew-list")
STATION_URL = reverse("train_station:station-list")
TRAIN_TYPE_URL = reverse("train_station:traintype-list")
TRAIN_URL = reverse("train_station:train-list")
ROUTE_URL = reverse("train_station:route-list")
JOURNEY_URL = reverse("train_station:journey-list")
ORDER_URL = reverse("train_station:order-list")


def detail_crew_url(crew_id):
    return reverse("train_station:crew-detail", args=[crew_id])


def detail_train_url(train_id):
    return reverse("train_station:train-detail", args=[train_id])


def detail_train_type_url(train_type_id):
    return reverse("train_station:train-type-detail", args=[train_type_id])


def detail_route_url(route_id):
    return reverse("train_station:route-detail", args=[route_id])


def detail_station_url(station_id):
    return reverse("train_station:station-detail", args=[station_id])


def detail_journey_url(journey_id):
    return reverse("train_station:journey-detail", args=[journey_id])


def detail_order_url(order_id):
    return reverse("train_station:order-detail", args=[order_id])


def sample_crew(**params):
    defaults = {
        "first_name": "Fred",
        "last_name": "Flintstone",
    }
    defaults.update(params)

    return Crew.objects.create(**params)


def sample_station(**params):
    defaults = {
        "name": "Central Station",
        "latitude": 50.0,
        "longitude": 2.0,
        "address": Address.objects.create(country="France", city="Paris"),
    }
    defaults.update(params)

    return Station.objects.create(**params)


def sample_train_type(**params):
    defaults = {
        "name": "TestTrainType",
    }
    defaults.update(params)

    return TrainType.objects.create(**params)


def sample_address(**params):
    defaults = {
        "country": "TestCountry",
        "city": "TestCity",
    }
    defaults.update(params)

    return Address.objects.create(**params)


def sample_route(**params):
    defaults = {
        "source": sample_station(
            name="TestSource", latitude=51.5, longitude=-0.13
        ),
        "destination": Station.objects.create(
            name="TestDestination", latitude=52.5, longitude=13.4
        ),
    }
    defaults.update(params)

    return Route.objects.create(**params)
