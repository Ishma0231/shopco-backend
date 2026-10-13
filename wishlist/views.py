from rest_framework.generics import (
    ListAPIView,CreateAPIView,DestroyAPIView)
from rest_framework.permissions import (IsAuthenticated)
from .serializers import (AddToWishlistSerializer,
                          ViewWishlistSerializer)
from rest_framework import status
from rest_framework.response import Response
from .models import Wishlist
from common.pagination import CustomPagination
from django.db.models import Prefetch
from products.models import ProductImage

# Create your views here.
class AddToWishlistAPIView(CreateAPIView):
    permission_classes=[IsAuthenticated]
    serializer_class=AddToWishlistSerializer

         
    def create(self,request,*args,**kwargs):
        serializer=self.get_serializer(
            data=request.data
        )

        serializer.is_valid(raise_exception=True)
        wishlist,created=Wishlist.objects.get_or_create(
            user=request.user,
            variant=serializer.validated_data["variant"]
        )
        if created:
            message="Added to Wishlist"
            
        else:
            message="Item Already in Wishlist"
        return Response({"message":message,
                         "wishlist_id":wishlist.id}
                        ,status=status.HTTP_200_OK)

        
        
class ViewWishListAPIView(ListAPIView):
    serializer_class=ViewWishlistSerializer
    permission_classes=[IsAuthenticated]
    pagination_class=CustomPagination

    def get_queryset(self):
        return Wishlist.objects.filter(
            user=self.request.user
        ).select_related(
            "variant__product"
        ).prefetch_related(
           Prefetch(
               "variant__product_color__images",
               queryset=ProductImage.objects.filter(
                   is_active=True,is_primary=True
               ),
               to_attr="primary_images"

           )
        )
    
class RemoveWishListAPIView(DestroyAPIView):
    permission_classes=[IsAuthenticated]

    def get_queryset(self):
        return Wishlist.objects.filter(
            user=self.request.user
        )
    def destroy(self,request,*args,**kwargs):
        obj=self.get_object()
        wishlist_id=obj.id
        self.perform_destroy(obj)
        return Response({
            "message":"Removed from Wishlist successfully!",
            "wishlist_id":wishlist_id
        },status=status.HTTP_200_OK)



