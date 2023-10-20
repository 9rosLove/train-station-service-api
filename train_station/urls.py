from rest_framework.routers import SimpleRouter

from train_station.views import (
    CrewViewSet,
    TrainTypeViewSet,
    StationViewSet,
    TrainViewSet,
    RouteViewSet,
)

router = SimpleRouter()

router.register("stations", StationViewSet)
router.register("crew", CrewViewSet)
router.register("train_types", TrainTypeViewSet)
router.register("routes", RouteViewSet)
router.register("trains", TrainViewSet)

urlpatterns = router.urls

app_name = "train_station"
