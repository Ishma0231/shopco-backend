from django.urls import path
from .views import (CreateAddressAPIView,ViewAddressAPIView,
                    EditAddressAPIView,DeleteAddressAPIView)

urlpatterns=[
    path("addresses/create/",CreateAddressAPIView.as_view()),
    path("addresses/<int:pk>/edit/",EditAddressAPIView.as_view()),
    path("addresses/<int:pk>/delete/",DeleteAddressAPIView.as_view()),
    path("addresses/",ViewAddressAPIView.as_view())
]