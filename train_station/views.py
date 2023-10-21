from rest_framework import viewsets

from train_station.models import Crew, Station, Train, TrainType, Route
from train_station.serializers import (
    CrewSerializer,
    StationSerializer,
    TrainTypeSerializer,
    TrainSerializer,
    RouteSerializer,
    RouteListSerializer,
    RouteDetailSerializer,
    TrainListRetrieveSerializer,
)


class StationViewSet(viewsets.ModelViewSet):
    queryset = Station.objects.all()
    serializer_class = StationSerializer


class CrewViewSet(viewsets.ModelViewSet):
    queryset = Crew.objects.all()
    serializer_class = CrewSerializer


class TrainTypeViewSet(viewsets.ModelViewSet):
    queryset = TrainType.objects.all()
    serializer_class = TrainTypeSerializer


class RouteViewSet(viewsets.ModelViewSet):
    queryset = Route.objects.all()
    serializer_class = RouteSerializer

    def get_serializer_class(self):
        if self.action == "list":
            return RouteListSerializer

        if self.action == "retrieve":
            return RouteDetailSerializer

        return self.serializer_class


class TrainViewSet(viewsets.ModelViewSet):
    queryset = Train.objects.all()
    serializer_class = TrainSerializer

    def get_serializer_class(self):
        if self.action in ("list", "retrieve"):
            return TrainListRetrieveSerializer
        return self.serializer_class
