from .views import (AddToCartAPIView,ViewCart,UpdateCartItemQuantityAPIView,
                    RemoveCartItemAPIView,ClearCartItemsAPIView)
from django.urls import path

urlpatterns =[
    path("",ViewCart.as_view()),
    path("add/",AddToCartAPIView.as_view()),
    path("items/<int:pk>/update/",UpdateCartItemQuantityAPIView.as_view()),
    path("items/<int:pk>/remove/",RemoveCartItemAPIView.as_view()),
    path("clear/",ClearCartItemsAPIView.as_view())
]