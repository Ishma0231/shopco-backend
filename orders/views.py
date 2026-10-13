from rest_framework.generics import (CreateAPIView,ListAPIView,
                                     RetrieveAPIView,UpdateAPIView)
from rest_framework.views import APIView
from rest_framework.permissions import (IsAuthenticated)
from .serializers import (CheckoutSerializer,ListOrderSerializer,
                          OrderDetailSerializer,OrderItemSerializer)
from django.core.exceptions import ValidationError
from .models import OrderItem,Order
from products.models import ProductVariant
from datetime import date,timedelta
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from django.shortcuts import get_object_or_404
from common.pagination import CustomPagination
# Create your views here.
class Checkout(APIView):
    permission_classes=[IsAuthenticated]
    
    def post(self,request):
        serializer=CheckoutSerializer(
            data=request.data,
            context={
                "request":request
            }
        )
        serializer.is_valid(raise_exception=True)
        
        return Response(
            {
                "message": "Checkout details validated successfully",
                "address": serializer.validated_data["address"].id,
                "payment_method": serializer.validated_data["payment_method"]
            },
            status=status.HTTP_200_OK
        )

class CreateOrderAPIView(APIView):
    permission_classes=[IsAuthenticated]

    @transaction.atomic
    def post(self,request):
        serializer=CheckoutSerializer(
            data=request.data,
            context={
                "request":request
            }
        )
        serializer.is_valid(raise_exception=True)
        payment_method=serializer.validated_data["payment_method"]
        address=serializer.validated_data["address"]
        cart=request.user.cart
        cart_items=cart.items.select_related(
            "variant",
            "variant__product",
            "variant__product_color__color",
            "variant__size"
        ).prefetch_related(
            "variant__product_color__images"
        )
        if not cart_items.exists():
            raise ValidationError({"message":"Cart is empty!"})
        
        total_price=0
        for item in cart_items:
            variant=item.variant
            if item.quantity < variant.min_order_quantity:
                raise ValidationError({
               "message":f"Minimum order quantity is" 
                f"{variant.min_order_quantity}"}
            )
                
            if item.quantity > variant.stock:
                raise ValidationError({"message":
                    f"Insufficient stock for "
                    f"{variant.product.name}"})
            item_price=(
                variant.discount_price
                if variant.discount_price
                else variant.price
            )
            total_price+=(
                item_price * item.quantity
            )

        if payment_method==Order.PaymentMethod.RAZORPAY:
            raise ValidationError({"message":"Razorpay not implemented yet"}) 

        order=Order.objects.create(
            user=request.user,
            full_name=address.full_name,
            phone_number=address.phone_number,
            street_address=address.street_address,
            address_type=address.address_type,
            landmark=address.landmark,
            city=address.city,
            state=address.state,
            country=address.country,
            postal_code=address.postal_code,
            payment_method=payment_method,
            total_price=total_price
        )

        for item in cart_items:
            variant=item.variant
            item_price=(
                variant.discount_price
                if variant.discount_price
                else variant.price
            )
            product_image=variant.product_color.images.filter(
                is_primary=True
            ).first()
            today=date.today()
            delivery_date=today + timedelta(
                days=variant.estimated_delivery_days
            )

            OrderItem.objects.create(
                order=order,
                variant=variant,
                product_name=variant.product.name,
                color_name=variant.product_color.color.hex_code,
                size_name=variant.size.name,
                price=item_price,
                quantity=item.quantity,
                product_image=product_image.image.url,
                estimated_delivery_date=delivery_date
            )
            variant.stock -= item.quantity
            variant.save()

        cart_items.delete()
        return Response({
            "message":"Order created successfully",
            "order_id":order.order_id,
        },status=status.HTTP_201_CREATED)


class ListOrderAPIView(ListAPIView):
    permission_classes=[IsAuthenticated]
    serializer_class=ListOrderSerializer
    pagination_class=CustomPagination

    def get_queryset(self):
        return Order.objects.filter(
            user=self.request.user
        ).prefetch_related("items").order_by("-created_at")
    
class OrderDetailAPIView(RetrieveAPIView):
    permission_classes=[IsAuthenticated]
    serializer_class=OrderDetailSerializer
    lookup_field="order_id"
    def get_queryset(self):
        return Order.objects.filter(
            user=self.request.user
        ).prefetch_related("items")
 
class CancelOrderItemAPIView(APIView):
    permission_classes=[IsAuthenticated]
    
    @transaction.atomic
    def patch(self,request,pk):
        item=get_object_or_404(
            OrderItem.objects.select_for_update(),
            pk=pk,
            order__user=request.user
        )
        if item.item_status in (OrderItem.ItemStatus.PENDING,OrderItem.ItemStatus.PROCESSING):
            item.item_status=OrderItem.ItemStatus.CANCELLED
        else:
            raise ValidationError({"message":"This item can no longer be cancelled."})
        variant=(
            ProductVariant.objects
            .select_for_update()
            .get(pk=item.variant_id)
            )
        variant.stock += item.quantity
        variant.save()
        item.save()
        order=get_object_or_404(
            Order.objects.select_for_update(),
            pk=item.order.pk
        )
        order.total_price-=(item.price*item.quantity)
        items=order.items.all()
        if (
            items.filter(item_status=OrderItem.ItemStatus.PROCESSING)
        ).exists():
            order.order_status=Order.OrderStatus.PROCESSING

        elif items.filter(
        item_status=OrderItem.ItemStatus.SHIPPED).exists():
           order.order_status = Order.OrderStatus.SHIPPED

        elif items.filter(
            item_status=OrderItem.ItemStatus.PENDING
        ).exists():
            order.order_status=Order.OrderStatus.PENDING

        elif items.filter(
            item_status=OrderItem.ItemStatus.DELIVERED
        ).exists():
            order.order_status=Order.OrderStatus.DELIVERED

        else:
            order.order_status=Order.OrderStatus.CANCELLED

        order.save()
        if order.payment_method==Order.PaymentMethod.RAZORPAY:
            message= (
                "Order item cancelled successfully. "
                "Any eligible refund will be processed to your original payment method."
           )
        else:
            message=(
                "Order item cancelled successfully."
            )

        return Response(
            {"message":message},status=status.HTTP_200_OK
        )

        
class CancelOrderAPIView(APIView):
    permission_classes=[IsAuthenticated]

    @transaction.atomic
    def patch(self,request,order_id):
        order=(
            Order.objects.
            select_for_update().
            get(
                order_id=order_id,
                user=request.user)
        )
        items=order.items.select_for_update()
        if not items.exists():
            raise ValidationError({"message":"Order items cannot be empty"})
        
        for item in items:
            if item.item_status not in (OrderItem.ItemStatus.PENDING,OrderItem.ItemStatus.PROCESSING):
                raise ValidationError({"message":"Order cannot be cancelled"})
            
            item.item_status=OrderItem.ItemStatus.CANCELLED
            variant=(
                ProductVariant.objects
                .select_for_update()
                .get(pk=item.variant_id)
                )
            variant.stock += item.quantity
            variant.save()
            item.save()

        order.total_price=0
        order.order_status=Order.OrderStatus.CANCELLED
        order.save()
        if order.payment_method==Order.PaymentMethod.RAZORPAY:
            message= (
                "Order cancelled successfully. "
                "Any eligible refund will be processed to your original payment method."
           )
        else:
            message=(
                "Order cancelled successfully."
            )

        return Response(
            {"message":message},status=status.HTTP_200_OK
        )

        




            
        