from django.test import TestCase

from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from django.urls import reverse
from rest_framework import status

from train_station.models import Crew
from train_station.serializers import CrewSerializer
from train_station.tests.samples import CREW_URL, sample_crew


def detail_url(crew_id):
    return reverse("train_station:crew-detail", args=[crew_id])


class UnAuthenticatedTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test__auth_required(self):
        response = self.client.get(CREW_URL)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedTests(TestCase):
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
        self.assertEqual(serializer.data, response.data["results"] )

    def test_retrieve_crew(self):
        crew = sample_crew()

        url = detail_url(crew.id)
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

        url = detail_url(crew.id)
        res = self.client.put(url, payload)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_crew_forbidden(self):
        crew = sample_crew()
        url = detail_url(crew.id)
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class AdminTests(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_superuser(
            email="user@te43st.com", password="pFDfsdf53assword"
        )
        self.client.force_authenticate(self.user)

    def test_crew_create(self):
        payload = {
            "first_name": "George",
            "last_name": "Oliver",
        }

        response = self.client.post(CREW_URL, payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["first_name"], payload["first_name"])
        self.assertEqual(response.data["last_name"], payload["last_name"])

    def test_crew_update(self):
        crew = sample_crew()
        payload = {
            "first_name": "Yoda",
            "last_name": "Luke",
        }

        url = detail_url(crew.id)
        response = self.client.put(url, payload)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["first_name"], payload["first_name"])

    def test_crew_delete(self):
        crew = sample_crew()
        url = detail_url(crew.id)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
