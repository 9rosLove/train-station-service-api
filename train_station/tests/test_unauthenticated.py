from django.test import TestCase

from rest_framework.test import APIClient
from rest_framework import status

from train_station.tests.samples import (
    CREW_URL,
    TRAIN_URL,
    ROUTE_URL,
    JOURNEY_URL,
    ORDER_URL,
    TRAIN_TYPE_URL,
)


URLS = (CREW_URL, TRAIN_URL, ROUTE_URL, JOURNEY_URL, ORDER_URL, TRAIN_TYPE_URL)


class UnAuthenticatedTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_list__auth_required(self):
        for url in URLS:
            response = self.client.get(url)
            self.assertEqual(
                response.status_code, status.HTTP_401_UNAUTHORIZED
            )

    def test_create__auth_required(self):
        for url in URLS:
            response = self.client.post(url)
            self.assertEqual(
                response.status_code, status.HTTP_401_UNAUTHORIZED
            )
