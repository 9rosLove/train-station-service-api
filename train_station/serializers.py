from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from train_station.models import Crew, Station, TrainType, Train, Route


class StationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Station
        fields = "__all__"


class CrewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Crew
        fields = "__all__"


class TrainTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrainType
        fields = "__all__"


class RouteSerializer(serializers.ModelSerializer):
    def validate(self, attrs):
        data = super(RouteSerializer, self).validate(attrs)
        Route.validate_station(data["source"], data["destination"], ValidationError)
        return data

    class Meta:
        model = Route
        fields = ("id", "source", "destination", "distance_in_kilometers")


class RouteListSerializer(RouteSerializer):
    source = serializers.SlugRelatedField(slug_field="name", queryset=Station.objects.all())
    destination = serializers.SlugRelatedField(slug_field="name", queryset=Station.objects.all())


class RouteDetailSerializer(RouteSerializer):
    source = StationSerializer(read_only=True)
    destination = StationSerializer(read_only=True)


class TrainSerializer(serializers.ModelSerializer):
    def validate(self, attrs):
        data = super(TrainSerializer, self).validate(attrs)
        Train.validate_name(data["name"], ValidationError)
        return data

    class Meta:
        model = Train
        fields = ("id", "name", "cargo_number", "places_in_cargo", "train_type", "capacity")


class TrainListRetrieveSerializer(TrainSerializer):
    train_type = serializers.SlugRelatedField(
        slug_field="name", queryset=TrainType.objects.all()
    )
