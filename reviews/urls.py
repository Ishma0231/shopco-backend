from django.urls import path
from .views import (
    CreateReviewAPIView,
    UpdateReviewAPIView,
    DeleteReviewAPIView,
    ListReviewAPIView,
    CreateReviewImageAPIView,
    DeleteReviewImageAPIView,GetMyReviewsAPIView,ListAllReviewsAPIView
  
)


urlpatterns=[
    path(
        "products/<slug:slug>/create/",
        CreateReviewAPIView.as_view(),
        name="review-create"
    ),
    
    path(
        "<int:pk>/update/",
        UpdateReviewAPIView.as_view(),
        name="review-update"
    ),

    path(
        "<int:pk>/delete/",
        DeleteReviewAPIView.as_view(),
        name="review-delete"
    ),

    path(
        "<int:pk>/images/create/",
        CreateReviewImageAPIView.as_view(),
        name="review-image-create"
    ),
   
    path(
        "images/<int:pk>/delete/",
        DeleteReviewImageAPIView.as_view(),
        name="review-image-delete"
    ),
    path("product/<slug:slug>/",
         ListReviewAPIView.as_view(),name="list-reviews"),

    path("product/<slug:slug>/my-reviews/",
        GetMyReviewsAPIView.as_view(),
        name="my-reviews"
         ),

    path("",
         ListAllReviewsAPIView.as_view(),
         name="all-reviews")
]