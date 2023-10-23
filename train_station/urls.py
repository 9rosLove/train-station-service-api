from rest_framework.routers import DefaultRouter

from train_station.views import (
    CrewViewSet,
    TrainTypeViewSet,
    StationViewSet,
    TrainViewSet,
    RouteViewSet,
    JourneyViewSet,
    OrderViewSet,
)

router = DefaultRouter()

router.register("stations", StationViewSet)
router.register("crew", CrewViewSet)
router.register("train_types", TrainTypeViewSet)
router.register("routes", RouteViewSet)
router.register("trains", TrainViewSet)
router.register("journeys", JourneyViewSet)
router.register("orders", OrderViewSet)

urlpatterns = router.urls

app_name = "train_station"
