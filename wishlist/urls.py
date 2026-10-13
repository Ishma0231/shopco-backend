from django.urls import path
from .views import (AddToWishlistAPIView,ViewWishListAPIView,
                    RemoveWishListAPIView)

urlpatterns=[
     path("",ViewWishListAPIView.as_view()),

     path("add/",AddToWishlistAPIView.as_view()),

     path("items/<int:pk>/remove/",RemoveWishListAPIView.as_view())
]
   