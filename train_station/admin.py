from django.contrib import admin

from .models import (
    Crew,
    Station,
    TrainType,
    Train,
    Route,
    Journey,
    Ticket,
    Order,
)

admin.site.register(Crew)
admin.site.register(Station)
admin.site.register(TrainType)
admin.site.register(Train)
admin.site.register(Route)
admin.site.register(Journey)
admin.site.register(Ticket)
admin.site.register(Order)
