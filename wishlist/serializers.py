from rest_framework import serializers
from .models import Wishlist


class AddToWishlistSerializer(serializers.ModelSerializer):
    class Meta:
        model=Wishlist
        fields=[
            "variant"
        ]

class ViewWishlistSerializer(serializers.ModelSerializer):
    product_name=serializers.CharField(
        source="variant.product.name",
        read_only=True
    )
    variant_id=serializers.IntegerField(
        read_only=True,
        source="variant.id"
    )
    product_slug=serializers.CharField(
        source="variant.product.slug",
        read_only=True
    )
    min_order_quantity=serializers.IntegerField(
        read_only=True,
        source="variant.min_order_quantity"
    )
    primary_image=serializers.SerializerMethodField()
    price=serializers.SerializerMethodField()
    stock=serializers.IntegerField(
        read_only=True,
        source="variant.stock"
    )
    class Meta:
        model=Wishlist
        fields=[
            "id",
            "product_name",
            "variant_id",
            "min_order_quantity",
            "primary_image",
            "price",
            "stock",
            "created_at",
            "product_slug"
        ]
    
    def get_primary_image(self,obj):
        image=obj.variant.product_color.images.filter(
            is_primary=True,
            is_active=True
        ).first()

        if image:
            return image.image.url
        return None
    
    def get_price(self,obj):
        price = obj.variant.discount_price or obj.variant.price
        return (
            str(price.amount)
           
        )
    
