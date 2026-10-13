from django.urls import path
from .views import (Checkout,CreateOrderAPIView,ListOrderAPIView,
                    OrderDetailAPIView,CancelOrderAPIView,CancelOrderItemAPIView,
                    )


urlpatterns=[
    path("",ListOrderAPIView.as_view()),
    path("checkout/",Checkout.as_view()),
    path("create/",CreateOrderAPIView.as_view()),
    path("<str:order_id>/",OrderDetailAPIView.as_view()),
    path("<str:order_id>/cancel/",CancelOrderAPIView.as_view()),
    path("items/<int:pk>/cancel/",CancelOrderItemAPIView.as_view())
]