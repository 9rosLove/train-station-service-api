from rest_framework.routers import SimpleRouter

from train_station.views import CrewViewSet, TrainTypeViewSet, StationViewSet

router = SimpleRouter()

router.register("stations", StationViewSet)
router.register("crew", CrewViewSet)
router.register("train_types", TrainTypeViewSet)

urlpatterns = router.urls
