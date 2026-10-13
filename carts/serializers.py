from rest_framework import serializers
from .models import Cart,CartItem
from django.db.models import Sum

class AddToCartSerializer(serializers.Serializer):
    variant_id=serializers.IntegerField(min_value=1)
    quantity=serializers.IntegerField(min_value=1)

class CartItemSerializer(serializers.ModelSerializer):
    product_id=serializers.IntegerField(
        source="variant.product.id",
        read_only=True
    )
    variant_id=serializers.IntegerField(
        source="variant.id",
        read_only=True
    )
    product_slug=serializers.CharField(
        source="variant.product.slug",
        read_only=True
    )
    product_name=serializers.CharField(
        source="variant.product.name",
        read_only=True
    )
    color = serializers.CharField(
        source="variant.product_color.color.hex_code",
        read_only=True
    )
    size = serializers.CharField(
        source="variant.size.name",
        read_only=True
    )
    primary_image=serializers.SerializerMethodField()
    subtotal=serializers.SerializerMethodField()
    price=serializers.SerializerMethodField()
    stock=serializers.IntegerField(
        source="variant.stock",
        read_only=True
    )
    min_order_quantity=serializers.IntegerField(
        source="variant.min_order_quantity",
        read_only=True
    )

    class Meta:
        model=CartItem
        fields=[
            "id",
            "product_id",
            "variant_id",
            "product_name",
            "primary_image",
            "subtotal",
            "quantity",
            "price", 
            "color",
            "size",
            "product_slug",
            "stock",
            "min_order_quantity"
        ]

    def get_primary_image(self,obj):
        image=obj.variant.product_color.images.filter(
            is_primary=True
        ).first()
        if image:
            return image.image.url
        
        return None
    
    def get_price(self,obj):
        price= obj.variant.discount_price or obj.variant.price 
        return (
           str(price.amount)
        )
    
    def get_subtotal(self,obj):
        price=(
            obj.variant.discount_price
            or
            obj.variant.price
        )
        item_price=price * obj.quantity

        return (str(item_price.amount))


class CartSerializer(serializers.ModelSerializer):
    items=CartItemSerializer(many=True,read_only=True)
    total=serializers.SerializerMethodField()
    count = serializers.SerializerMethodField()
    class Meta:
        model=Cart
        fields=[
            "id",
            "items",
            "count",
            "total"
        ]

    def get_total(self,obj):
        total=0
        for item in obj.items.all():
            price=(
                item.variant.discount_price
                or
                item.variant.price
            )
            total+=price * item.quantity
        return (str(total.amount))

    def get_count(self,obj):
        return obj.items.aggregate(
            total_items=Sum("quantity")
        )["total_items"] or 0

  


class UpdateCartItemSerializer(serializers.Serializer):
    quantity=serializers.IntegerField(
        min_value=1
        )