from django.urls import reverse

from train_station.models import TrainType, Train, Crew, Station, Address, Route, Ticket, Order, Journey

CREW_URL = reverse("train_station:crew-list")
STATION_URL = reverse("train_station:station-list")
TRAIN_URL = reverse("train_station:train-list")
ROUTE_URL = reverse("train_station:route-list")
JOURNEY_URL = reverse("train_station:journey-list")
ORDER_URL = reverse("train_station:order-list")


def sample_crew(**params):
    defaults = {
        "first_name": "John",
        "last_name": "Doe",
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


def sample_train(**params):
    defaults = {
        "name": "JGY04958",
        "train_type": TrainType.objects.first(),
    }
    defaults.update(params)

    return Train.objects.create(**params)


def sample_train_type(**params):
    defaults = {
        "name": "cargo",
    }
    return TrainType.objects.create(**params)


def sample_address(**params):
    defaults = {
        "country": "Belgium",
        "city": "Brussels",
    }
    defaults.update(params)

    return Address.objects.create(**params)


def sample_route(**params):
    defaults = {
        "source": sample_station(name="Hamburg"),
        "destination": sample_station(name="Berlin"),
    }
    defaults.update(params)

    return Route.objects.create(**params)
