from django.test import TestCase

from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status

from train_station.models import (
    Crew,
    TrainType,
    Station,
    Address,
    Train, Route,
)
from train_station.serializers import (
    CrewSerializer,
    StationSerializer,
    TrainTypeSerializer,
)
from train_station.tests.samples import (
    CREW_URL,
    sample_crew,
    sample_train_type,
    sample_station,
    STATION_URL,
    detail_station_url,
    TRAIN_TYPE_URL,
    detail_crew_url,
    sample_address,
    TRAIN_URL,
    detail_train_url,
)


class TestAuthenticatedCrewTests(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="user@te43st.com", password="pFDfsdf53assword"
        )
        self.client.force_authenticate(self.user)

    def test_list_crew(self):
        sample_crew()
        sample_crew(first_name="Bob", last_name="Loblaw")
        response = self.client.get(CREW_URL)
        crew_list = Crew.objects.all()
        serializer = CrewSerializer(crew_list, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(serializer.data, response.data["results"])

    def test_retrieve_crew(self):
        crew = sample_crew()

        url = detail_crew_url(crew.id)
        response = self.client.get(url)
        serializer = CrewSerializer(crew)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_create_crew_forbidden(self):
        payload = {
            "first_name": "Harry",
            "last_name": "Oliver",
        }

        res = self.client.post(CREW_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_crew_forbidden(self):
        crew = sample_crew()
        payload = {
            "first_name": "Yoda",
            "last_name": "Luke",
        }

        url = detail_crew_url(crew.id)
        res = self.client.put(url, payload)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_crew_forbidden(self):
        crew = sample_crew()
        url = detail_crew_url(crew.id)
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class AuthenticatedTrainTypeTests(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="user@te43st.com", password="pFDfsdf53assword"
        )
        self.client.force_authenticate(self.user)

    def test_list_train_type(self):
        sample_train_type()
        sample_train_type(name="qwerty")
        response = self.client.get(TRAIN_TYPE_URL)
        trains = TrainType.objects.all()
        serializer = TrainTypeSerializer(trains, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(serializer.data, response.data["results"])

    def test_create_train_type_forbidden(self):
        payload = {
            "name": "Cold",
        }

        response = self.client.post(TRAIN_TYPE_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_train_type_forbidden(self):
        train_type = sample_train_type()
        payload = {
            "name": "Hot",
        }

        response = self.client.put(detail_station_url(train_type.id), payload)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_train_type_forbidden(self):
        train_type = sample_train_type()

        response = self.client.delete(detail_station_url(train_type.id))

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class AuthenticatedStationTests(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="user@te43st.com", password="pFDfsdf53assword"
        )
        self.client.force_authenticate(self.user)

    def test_list_station(self):
        address1 = sample_address(country="Test", city="Test")
        address2 = sample_address(country="Ukraine", city="Kyiv")
        sample_station(
            name="Boston Railway Station",
            latitude=89.0,
            longitude=89.0,
            address=address1,
        )
        sample_station(
            name="Kyiv", latitude=50.0, longitude=30.0, address=address2
        )
        response = self.client.get(STATION_URL)
        stations = Station.objects.all()
        serializer = StationSerializer(stations, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(serializer.data, response.data["results"])

    def test_retrieve_station(self):
        address = sample_address(country="France", city="Paris")
        station = sample_station(
            name="Paris Main Station",
            latitude=48.8566,
            longitude=2.3522,
            address=address,
        )
        url = detail_station_url(station.id)
        response = self.client.get(url)
        serializer = StationSerializer(station)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_create_station_forbidden(self):
        payload = {
            "name": "Paris Main Station",
            "latitude": 48.8566,
            "longitude": 2.3522,
            "address": Address.objects.create(country="France", city="Paris"),
        }
        response = self.client.post(STATION_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_station_forbidden(self):
        address = sample_address(country="France", city="Paris")
        station = sample_station(
            name="New York Railway Station",
            latitude=43.563,
            longitude=46.1,
            address=address,
        )
        payload = {
            "name": "Paris Main Station",
            "latitude": 48.8566,
            "longitude": 2.3522,
            "address": Address.objects.create(country="France", city="Paris"),
        }

        url = detail_station_url(station.id)
        response = self.client.put(url, payload)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_station_forbidden(self):
        address = sample_address(country="France", city="Paris")
        station = sample_station(
            name="Paris Main Station",
            latitude=48.8566,
            longitude=2.3522,
            address=address,
        )

        url = detail_station_url(station.id)
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class AuthenticatedTrainTests(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="user@te43st.com", password="Password123"
        )
        self.client.force_authenticate(self.user)

    def test_list_train(self):
        train_type1 = sample_train_type(name="forks")
        train_type2 = sample_train_type(name="goods")
        Train.objects.create(
            name="JHG48576",
            train_type=train_type1,
            cargo_number=5,
            places_in_cargo=35,
        )
        Train.objects.create(
            name="JHG53585",
            train_type=train_type2,
            cargo_number=5,
            places_in_cargo=35,
        )

        response = self.client.get(TRAIN_URL)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_train(self):
        train_type = sample_train_type(name="cool")
        train = Train.objects.create(
            name="JHG48576",
            train_type=train_type,
            cargo_number=5,
            places_in_cargo=35,
        )
        url = detail_train_url(train.id)
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_train_forbidden(self):
        train_type = sample_train_type()
        payload = {
            "name": "JHG48576",
            "cargo_number": "5",
            "places_in_cargo": 35,
            "train_type": train_type,
        }
        response = self.client.post(TRAIN_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_train_forbidden(self):
        train_type = sample_train_type()
        train = Train.objects.create(
            name="JHG48576",
            train_type=train_type,
            cargo_number=5,
            places_in_cargo=35,
        )
        payload = {
            "name": "JHG48576",
            "cargo_number": "5",
            "places_in_cargo": 35,
            "train_type": train.train_type,
        }

        url = detail_train_url(train.id)
        response = self.client.put(url, payload)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
