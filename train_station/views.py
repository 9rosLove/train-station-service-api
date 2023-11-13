from datetime import datetime

from django.db.models import Count, F
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.exceptions import ParseError
from rest_framework.mixins import CreateModelMixin
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response

from train_station.models import (
    Crew,
    Station,
    Train,
    TrainType,
    Route,
    Order,
    Journey,
)
from train_station.pagintation import (
    StationPagination,
    CrewPagination,
    TrainTypePagination,
    RoutePagination,
    TrainPagination,
    JourneyPagination,
    OrderPagination,
)
from train_station.permissions import IsAdminOrIfAuthenticatedReadOnly
from train_station.serializers import (
    CrewSerializer,
    StationSerializer,
    TrainTypeSerializer,
    TrainSerializer,
    RouteSerializer,
    RouteListSerializer,
    RouteDetailSerializer,
    TrainListRetrieveSerializer,
    OrderDetailSerializer,
    OrderListSerializer,
    OrderSerializer,
    JourneyDetailSerializer,
    JourneyListSerializer,
    JourneySerializer,
    StationImageSerializer,
)


class StationViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    CreateModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Station.objects.all()
    serializer_class = StationSerializer
    pagination_class = StationPagination
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)

    def get_serializer_class(self):
        if self.action == "upload_image":
            return StationImageSerializer
        return self.serializer_class

    @action(
        methods=["POST"],
        detail=True,
        url_path="upload-image",
        permission_classes=[IsAdminUser],
    )
    def upload_image(self, request, pk=None):
        station = self.get_object()
        serializer = self.get_serializer(station, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class CrewViewSet(viewsets.ModelViewSet):
    queryset = Crew.objects.all()
    serializer_class = CrewSerializer
    pagination_class = CrewPagination
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)


class TrainTypeViewSet(
    mixins.ListModelMixin,
    CreateModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    queryset = TrainType.objects.all()
    serializer_class = TrainTypeSerializer
    pagination_class = TrainTypePagination
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)


class RouteViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Route.objects.all()
    serializer_class = RouteSerializer
    pagination_class = RoutePagination
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)

    def get_serializer_class(self):
        if self.action == "list":
            return RouteListSerializer

        if self.action == "retrieve":
            return RouteDetailSerializer

        return self.serializer_class


class TrainViewSet(viewsets.ModelViewSet):
    queryset = Train.objects.all()
    serializer_class = TrainSerializer
    pagination_class = TrainPagination
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)

    @staticmethod
    def _params_to_ints(qs):
        return [int(str_id) for str_id in qs.split(",")]

    def get_queryset(self):
        queryset = self.queryset

        train_type = self.request.query_params.get("train_type", None)

        if train_type:
            train_type_ids = self._params_to_ints(train_type)
            queryset = queryset.filter(train_type__id__in=train_type_ids)

        return queryset

    def get_serializer_class(self):
        if self.action in ("list", "retrieve"):
            return TrainListRetrieveSerializer

        return self.serializer_class

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "train_type",
                description="Filter by train type",
                type=OpenApiTypes.STR,
            )
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(self, request, *args, **kwargs)


class JourneyViewSet(viewsets.ModelViewSet):
    queryset = (
        Journey.objects.all()
        .select_related("route", "train")
        .annotate(
            tickets_available=(
                F("train__cargo_number") * F("train__places_in_cargo")
                - Count("tickets")
            )
        )
    )
    serializer_class = JourneySerializer
    pagination_class = JourneyPagination
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)

    def get_queryset(self):
        queryset = self.queryset

        source = self.request.query_params.get("source", None)
        destination = self.request.query_params.get("destination", None)
        departure_date = self.request.query_params.get("date", None)
        departure_time = self.request.query_params.get("time", None)

        if source:
            queryset = queryset.filter(route__source__name__icontains=source)

        if destination:
            queryset = queryset.filter(
                route__destination__name__icontains=destination
            )

        if departure_date:
            try:
                date = datetime.strptime(departure_date, "%Y-%m-%d").date()
            except ValueError:
                raise ParseError(
                    detail="Invalid date format. Please use YYYY-MM-DD."
                )
            queryset = queryset.filter(departure_time__date=date)
            if departure_time:
                try:
                    time = datetime.strptime(departure_time, "%H:%M").time()
                except ValueError:
                    raise ParseError(
                        detail="Invalid time format. Please use HH:MM."
                    )
                queryset = queryset.filter(departure_time__time=time)

        return queryset.distinct()

    def get_serializer_class(self):
        if self.action == "list":
            return JourneyListSerializer

        if self.action == "retrieve":
            return JourneyDetailSerializer

        return self.serializer_class

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "source",
                description="Filter by source",
                type=OpenApiTypes.STR,
            ),
            OpenApiParameter(
                "destination",
                description="Filter by destination",
                type=OpenApiTypes.STR,
            ),
            OpenApiParameter(
                "date",
                description="Filter by date",
                type=OpenApiTypes.DATE,
            ),
            OpenApiParameter(
                "time",
                description="Filter by time",
                type=OpenApiTypes.TIME,
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(self, request, *args, **kwargs)


class OrderViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    pagination_class = OrderPagination
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        queryset = self.queryset.filter(user=self.request.user)

        departure_date = self.request.query_params.get("date", None)
        departure_time = self.request.query_params.get("time", None)

        if departure_date:
            try:
                date = datetime.strptime(departure_date, "%Y-%m-%d").date()
                queryset = queryset.filter(
                    tickets_journey__departure_time__date=date
                )
            except ValueError:
                raise ParseError(
                    detail="Invalid date format. Please use YYYY-MM-DD."
                )
            if departure_time:
                try:
                    time = datetime.strptime(departure_time, "%H:%M").time()
                    queryset = queryset.filter(
                        tickets__journey__departure_time__time=time
                    )
                except ValueError:
                    raise ParseError(
                        detail="Invalid time format. Please use HH:MM."
                    )

        return queryset

    def get_serializer_class(self):
        if self.action == "list":
            return OrderListSerializer

        if self.action == "retrieve":
            return OrderDetailSerializer

        return self.serializer_class

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "date",
                description="Filter by date",
                type=OpenApiTypes.DATE,
            ),
            OpenApiParameter(
                "time",
                description="Filter by time",
                type=OpenApiTypes.TIME,
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(self, request, *args, **kwargs)
