from django.db import transaction
from geopy import Nominatim
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.fields import CharField

from train_station.models import (
    Crew,
    Station,
    TrainType,
    Train,
    Route,
    Journey,
    Ticket,
    Order,
    Address,
)


class StationSerializer(serializers.ModelSerializer):
    address = CharField(source="address.__str__", read_only=True)

    def get_address(self, validated_data):
        geolocator = Nominatim(user_agent="train_station")
        latitude = self.validated_data["latitude"]
        longitude = self.validated_data["longitude"]
        location_info = geolocator.reverse(f"{latitude},{longitude}")
        address = dict()

        if location_info:
            address_raw = location_info.raw["address"]
            address["country"] = address_raw.get("country")
            address["city"] = address_raw.get("city")
            if not address["city"]:
                if "town" in address_raw:
                    address["city"] = address_raw["town"]
                elif "village" in address_raw:
                    address["city"] = address_raw["village"]

            return address

    def create(self, validated_data):
        address = self.get_address(validated_data)
        r_address = Address.objects.create(**address)
        station = Station.objects.create(**validated_data, address=r_address)

        return station

    class Meta:
        model = Station
        fields = ("id", "name", "latitude", "longitude", "address")


class StationImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Station
        fields = ("image",)


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
        Route.validate_station(
            data["source"], data["destination"], ValidationError
        )
        return data

    class Meta:
        model = Route
        fields = ("id", "source", "destination", "distance_in_kilometers")


class RouteListSerializer(RouteSerializer):
    source = serializers.SlugRelatedField(
        slug_field="name", queryset=Station.objects.all()
    )
    destination = serializers.SlugRelatedField(
        slug_field="name", queryset=Station.objects.all()
    )


class RouteDetailSerializer(RouteSerializer):
    source = StationSerializer(read_only=True)
    destination = StationSerializer(read_only=True)


class TrainSerializer(serializers.ModelSerializer):
    class Meta:
        model = Train
        fields = (
            "id",
            "name",
            "cargo_number",
            "places_in_cargo",
            "train_type",
            "capacity",
        )

    def validate(self, attrs):
        data = super(TrainSerializer, self).validate(attrs)
        Train.validate_name(data["name"], ValidationError)

        return data


class TrainListRetrieveSerializer(TrainSerializer):
    train_type = serializers.SlugRelatedField(
        slug_field="name", queryset=TrainType.objects.all()
    )


class JourneySerializer(serializers.ModelSerializer):
    tickets_available = serializers.IntegerField(read_only=True)

    class Meta:
        model = Journey
        fields = (
            "id",
            "departure_time",
            "arrival_time",
            "route",
            "train",
            "tickets_available",
            "crew",
        )

    def validate(self, attrs):
        data = super(JourneySerializer, self).validate(attrs)
        Journey.validate_time(
            attrs["departure_time"], attrs["arrival_time"], ValidationError
        )
        Journey.validate_train(
            attrs["train"],
            attrs["departure_time"],
            attrs["arrival_time"],
            ValidationError,
        )

        return data


class JourneyListSerializer(JourneySerializer):
    route = serializers.CharField(source="route.__str__", read_only=True)
    train = serializers.SlugRelatedField(
        slug_field="name", queryset=Train.objects.all()
    )
    crew = serializers.SlugRelatedField(
        slug_field="full_name", queryset=Crew.objects.all(), many=True
    )


class TicketSeatsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = ("cargo", "seat")


class JourneyDetailSerializer(JourneyListSerializer):
    route = RouteListSerializer()
    train = TrainListRetrieveSerializer()
    taken_seats = TicketSeatsSerializer(
        source="tickets", many=True, read_only=True
    )

    class Meta:
        model = Journey
        fields = (
            "id",
            "route",
            "train",
            "departure_time",
            "arrival_time",
            "crew",
            "taken_seats",
        )


class TicketSerializer(serializers.ModelSerializer):
    def validate(self, attrs):
        data = super(TicketSerializer, self).validate(attrs)
        Ticket.validate_seat(
            attrs["seat"],
            attrs["journey"].train.places_in_cargo,
            ValidationError,
        )
        Ticket.validate_cargo(
            attrs["cargo"],
            attrs["journey"].train.cargo_number,
            ValidationError,
        )

        return data

    class Meta:
        model = Ticket
        fields = ("id", "cargo", "seat", "journey")


class TicketListSerializer(TicketSerializer):
    journey = serializers.CharField(source="journey.__str__", read_only=True)


class TicketDetailSerializer(TicketSerializer):
    journey = JourneyDetailSerializer()


class OrderSerializer(serializers.ModelSerializer):
    tickets = TicketSerializer(many=True, allow_empty=False)

    class Meta:
        model = Order
        fields = ("id", "tickets", "created_at")

    def create(self, validated_data):
        with transaction.atomic():
            tickets_data = validated_data.pop("tickets")
            order = Order.objects.create(**validated_data)
            for ticket_data in tickets_data:
                Ticket.objects.create(order=order, **ticket_data)
            return order


class OrderListSerializer(OrderSerializer):
    tickets = TicketListSerializer(many=True, read_only=True)


class OrderDetailSerializer(OrderSerializer):
    tickets = TicketDetailSerializer(many=True, read_only=True)
