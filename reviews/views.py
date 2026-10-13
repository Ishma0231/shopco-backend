from .serializers import (ReviewCreateSerializer,ReviewUpdateSerializer,
                                      ReviewImageBulkCreateSerializer, ListReviewSerializer,ReviewImageSerializer)
from rest_framework.generics import (CreateAPIView,DestroyAPIView,
                                     UpdateAPIView,ListAPIView)
from rest_framework.permissions import (IsAuthenticated)
from django.shortcuts import get_object_or_404
from products.models import Product
from .models import Reviews,ReviewImage
from rest_framework.permissions import (IsAuthenticated,AllowAny)
from common.pagination import CustomPagination
from products.models import Product
from rest_framework.filters import OrderingFilter
from rest_framework.parsers import MultiPartParser,FormParser

# Create your views here.
class ListReviewAPIView(ListAPIView):
    pagination_class=CustomPagination
    permission_classes=[AllowAny]
    serializer_class=ListReviewSerializer
    filter_backends=[OrderingFilter]
    ordering_fields=[
        "rating",
        "created_at"
    ]
    ordering=[
        "-created_at"
    ]

    def get_queryset(self):
        product=get_object_or_404(
            Product,
            slug=self.kwargs["slug"])
        return (Reviews.objects.filter(product=product)
                .select_related("user")
                .prefetch_related("images"))

class ListAllReviewsAPIView(ListAPIView):
    pagination_class = CustomPagination
    permission_classes = [AllowAny]
    serializer_class = ListReviewSerializer
    filter_backends = [OrderingFilter]
    ordering_fields = [
        "rating",
        "created_at"
    ]
    ordering = [
        "-created_at"
    ]

    def get_queryset(self):
        return (
            Reviews.objects
            .select_related("user", "product")
            .prefetch_related("images")
        )

class CreateReviewAPIView(CreateAPIView):
    permission_classes=[IsAuthenticated]
    serializer_class=ReviewCreateSerializer
    parser_classes=[MultiPartParser,FormParser]
    def perform_create(self, serializer):
        product=get_object_or_404(
            Product,
            slug=self.kwargs["slug"]
        )
        serializer.save(
            product=product,
            user=self.request.user
        )

class UpdateReviewAPIView(UpdateAPIView):
    serializer_class=ReviewUpdateSerializer
    permission_classes=[IsAuthenticated]

    def get_queryset(self):
        return Reviews.objects.filter(
            user=self.request.user
        )



class DeleteReviewAPIView(DestroyAPIView):
    permission_classes=[IsAuthenticated]
    
    def get_queryset(self):
        return Reviews.objects.filter(
            user=self.request.user
        )


class CreateReviewImageAPIView(CreateAPIView):
    serializer_class=ReviewImageBulkCreateSerializer
    permission_classes=[IsAuthenticated]
    parser_classes=[MultiPartParser,FormParser]

    def get_serializer_context(self):
        context=super().get_serializer_context()
        review=get_object_or_404(
            Reviews,
            pk=self.kwargs["pk"],
            user=self.request.user
        )
        context["review"]=review
        return context
 
class DeleteReviewImageAPIView(DestroyAPIView):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return ReviewImage.objects.filter(
            review__user=self.request.user
        )

    def perform_destroy(self, instance):
        if instance.image:
            instance.image.delete(save=False)

        instance.delete()

class GetMyReviewsAPIView(ListAPIView):
    permission_classes=[IsAuthenticated]
    serializer_class=ListReviewSerializer

    def get_queryset(self):
        return (
            Reviews.objects.filter(
                user=self.request.user,
                product__slug=self.kwargs["slug"]
            ).select_related("user").prefetch_related("images")
        )