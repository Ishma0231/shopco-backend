from rest_framework import serializers
from users.models import Address
from .models import Order,OrderItem

class CheckoutSerializer(serializers.Serializer):
    address=serializers.PrimaryKeyRelatedField(
        queryset=Address.objects.all()
    )
    payment_method=serializers.ChoiceField(
        choices=Order.PaymentMethod.choices
    )
    
    def validate_address(self,value):
        request=self.context["request"]
        if not value.user==request.user:
            raise serializers.ValidationError({"message":"Invalid address"})
        
        return value
    def validate_payment_method(self,value):
        if value==Order.PaymentMethod.RAZORPAY:
            raise serializers.ValidationError(
               {"message": "Razor pay mot implemented yet"}
            )
        return value

class ListOrderSerializer(serializers.ModelSerializer):
    count=serializers.SerializerMethodField()
    total_price=serializers.SerializerMethodField()
    class Meta:
        model=Order
        fields=[
            "id",
            "order_id",
            "payment_method",
            "payment_status",
            "order_status",
            "total_price",
            "created_at",
            "count"
        ]
    def get_count(self,obj):
        return obj.items.exclude(
            item_status=OrderItem.ItemStatus.CANCELLED
        ).count()

    def get_total_price(self,obj):
        return (str(obj.total_price.amount))

class OrderItemSerializer(serializers.ModelSerializer):
    subtotal=serializers.SerializerMethodField()
    price=serializers.SerializerMethodField()
    class Meta:
        model=OrderItem
        fields=[
            "id",
            "variant",
            "product_name",
            "color_name",
            "size_name",
            "price",
            "quantity",
            "product_image",
            "estimated_delivery_date",
            "created_at",
            "item_status",
            "subtotal"
        ]

    def get_subtotal(self,obj):
        return str((obj.price*obj.quantity).amount)

    def get_price(self,obj):
        return (str(obj.price.amount))


class OrderDetailSerializer(serializers.ModelSerializer):
    items=OrderItemSerializer(many=True)
    address=serializers.SerializerMethodField()
    total_price=serializers.SerializerMethodField()
    class Meta:
        model=Order
        fields=[
            "order_id",
            "address",
            "payment_method",
            "payment_status",
            "order_status",
            "total_price",
            "items",
            "created_at"
        ]

    def get_address(self,obj):
        return {
            "full_name":obj.full_name,
            "phone_number":str(obj.phone_number),
            "street_address":obj.street_address,
            "address_type":obj.address_type,
            "landmark":obj.landmark,
            "city":obj.city,
            "state":obj.state,
            "country":str(obj.country),
            "postal_code":obj.postal_code
        }

    def get_total_price(self,obj):
        return (str(obj.total_price.amount))
