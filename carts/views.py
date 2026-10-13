from rest_framework.generics import (
                 CreateAPIView,RetrieveAPIView,UpdateAPIView,DestroyAPIView)
from rest_framework.permissions import (IsAuthenticated)
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import ValidationError
from .models import (
    Cart,CartItem
)
from products.models import (
    ProductVariant
)
from .serializers import (AddToCartSerializer,CartSerializer,UpdateCartItemSerializer)
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Prefetch

class AddToCartAPIView(APIView):
    permission_classes=[IsAuthenticated]

    def post(self,request):
        serializer=AddToCartSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        cart,created=Cart.objects.get_or_create(
            user=self.request.user
        )
        variant=get_object_or_404(
            ProductVariant,
            id=serializer.validated_data["variant_id"]
        )
        quantity=serializer.validated_data["quantity"]

        if (quantity<variant.min_order_quantity):
            raise ValidationError({
              "message":f"Minimum order quantity is {variant.min_order_quantity}"
            })
        if (quantity>variant.stock):
            raise ValidationError({"message":"Not enough stock"})
        
        cart_item=CartItem.objects.filter(
            variant=variant,
            cart=cart
        ).first()
        if cart_item:
            if(
                cart_item.quantity 
                + quantity > variant.stock
            ):
                raise ValidationError({"message":"Not enough stock"})
            
            cart_item.quantity+=quantity
            cart_item.save()
        else:
            CartItem.objects.create(
                cart=cart,
                variant=variant,
                quantity=quantity
            )
        return Response({
            "message":"Item added to cart successfully."
        },status=status.HTTP_200_OK)

class ViewCart(RetrieveAPIView):
    permission_classes=[IsAuthenticated]
    serializer_class=CartSerializer

    def get_object(self):
        cart,created=Cart.objects.get_or_create(
            user=self.request.user
        )
        if created:
            return cart
        
        return Cart.objects.prefetch_related(
            Prefetch(
                "items",
                queryset=CartItem.objects
                .select_related(
                    "variant__size",
                    "variant__product_color",
                    "variant__product"
                    )
                    .prefetch_related(
                        "variant__product_color__images"
                    )
            )
        ).get(pk=cart.pk)
            


class UpdateCartItemQuantityAPIView(UpdateAPIView):
    permission_classes=[IsAuthenticated]
    serializer_class=UpdateCartItemSerializer

    def get_queryset(self):
        return CartItem.objects.filter(
            cart__user=self.request.user
        )
    
    def perform_update(self,serializer):
        cart_item=self.get_object()
        quantity=serializer.validated_data["quantity"]
        variant=cart_item.variant

        if ( 
            quantity < variant.min_order_quantity
            ):
            raise ValidationError({
                "message":f"Minimum order quantity is {variant.min_order_quantity}"
            })
        if (
            quantity > variant.stock
        ):
            raise ValidationError({"message":"Not enough stock"})
        
        cart_item.quantity=quantity
        cart_item.save()

class RemoveCartItemAPIView(DestroyAPIView):
    permission_classes=[IsAuthenticated]

    def get_queryset(self):
        return CartItem.objects.filter(
            cart__user=self.request.user
        )
    
class ClearCartItemsAPIView(APIView):
    permission_classes=[IsAuthenticated]

    def delete(self,request):
        cart=Cart.objects.filter(
            user=request.user
        ).first()
        if not cart:
            raise ValidationError({"message":"Cart doesn't exist"})
        
        cart.items.all().delete()

        return Response(
            {"message":"Cart cleared successfully."},
            status=status.HTTP_200_OK)