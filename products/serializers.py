from rest_framework import serializers  
from .models import (Product,ProductImage,ProductType,ProductVariant,Size,Style,
                     Brand,Category,Color,Gender,ProductColor
                     )           
from reviews.serializers import ReviewSerializer
from wishlist.models import Wishlist


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model=Category
        fields="__all__"
        read_only_fields=["slug"]

class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model=Brand
        fields="__all__"
        read_only_fields=["slug"]

class ProductTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model=ProductType
        fields="__all__"
        read_only_fields=["slug"]

class GenderSerializer(serializers.ModelSerializer):
    class Meta:
        model=Gender
        fields="__all__"
        read_only_fields=["slug"]
        
class ColorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Color
        fields = [
            "id",
            "name",
            "slug",
            "hex_code",
        ]
        read_only_fields=["slug"]

class SizeSerializer(serializers.ModelSerializer):
    class Meta:
        model=Size
        fields="__all__"
        read_only_fields=["slug"]

class StyleSerializer(serializers.ModelSerializer):
    class Meta:
        model=Style
        fields="__all__"
        read_only_fields=["slug"]

class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model=ProductImage
        fields=[
                "id",
                "image",
                "alt_text",
                "is_primary"
                ]

#variant create     
class ProductVariantCreateSerializer(serializers.ModelSerializer):
    discount_price=serializers.DecimalField( 
        max_digits=10,
        decimal_places=2,
        required=False,
        allow_null=True)
    class Meta:
        model=ProductVariant
        fields=[
            "product_color",
            "size",
            "price",
            "discount_price",
            "min_order_quantity",
            "estimated_delivery_days",
            "stock",
        ]
    
    
class ProductVariantSerializer(serializers.ModelSerializer):
    sku = serializers.CharField(read_only=True)
    wishlisted_data = serializers.SerializerMethodField()

    price = serializers.SerializerMethodField()
    discount_price = serializers.SerializerMethodField()

    color = ColorSerializer(
        source="product_color.color",
        read_only=True
    )

    size = SizeSerializer(read_only=True)

    class Meta:
        model = ProductVariant
        fields = [
            "id",
            "color",
            "size",
            "price",
            "discount_price",
            "stock",
            "min_order_quantity",
            "estimated_delivery_days",
            "wishlisted_data",
            "sku",
        ]

    def get_price(self, obj):
        return str(obj.price.amount) if obj.price else None

    def get_discount_price(self, obj):
        return str(obj.discount_price.amount) if obj.discount_price else None

    def get_wishlisted_data(self, obj):
        request = self.context.get("request")

        if not request or not request.user.is_authenticated:
            return False

        wishlist = Wishlist.objects.filter(
            user=request.user,
            variant=obj
        ).first()

        return {
            "is_wishlisted": wishlist is not None,
            "wishlist_id": wishlist.id if wishlist else None
        }
    
class ProductColorSerializer(serializers.ModelSerializer):
    color=ColorSerializer(
        read_only=True
    )
    images=ProductImageSerializer(
        read_only=True,
        many=True
    )
    class Meta:
        model=ProductColor
        fields=[
            "id",
            "color",
            "images"
        ]
        

class ProductVariantUpdateSerializer(serializers.ModelSerializer):
    discount_price=serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=False,
        allow_null=True
    )
    class Meta:
        model=ProductVariant
        fields=[
                "product_color",
                "size",
                "price",
                "discount_price",
                "stock",
                "min_order_quantity",
                "estimated_delivery_days",
        ]

class ProductListSerializer(
    serializers.ModelSerializer):
    slug = serializers.SlugField(
        read_only=True
    )
    primary_image = serializers.SerializerMethodField()
    price=serializers.SerializerMethodField()
    discount_price=serializers.SerializerMethodField()
    featured_variant_id=serializers.SerializerMethodField()
    wishlist_data=serializers.SerializerMethodField()
    brand_name=serializers.CharField(
        source="brand.name",
        read_only=True
    )
    brand_slug=serializers.CharField(
        source="brand.slug",
        read_only=True
    )
    stock=serializers.SerializerMethodField()
    min_order_quantity=serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "slug",
            "price",
            "description",
            "featured_variant_id",
            "discount_price",
            "is_featured",
            "is_new_arrival",
            "wishlist_data",
            "primary_image",
            "brand_name",
            "brand_slug",
            "stock",
            "min_order_quantity"
        ]

    
    def get_featured_variant(self,obj):
        variants=obj.variants.filter(
            is_active=True
        )
        if not variants.exists():
            return None
        return min(
            variants,
            key=lambda variant:(
                variant.discount_price
                if variant.discount_price
                else variant.price
            )
        )

    def get_min_order_quantity(self,obj):
        variant=self.get_featured_variant(obj)
        return variant.min_order_quantity if variant else None

    def get_stock(self,obj):
        variant=self.get_featured_variant(obj)
        return variant.stock if variant else None
    
    def get_wishlist_data(self,obj):
        request=self.context.get("request")
        if (
            not request or
            not request.user.is_authenticated
        ):
            return None
        variant=self.get_featured_variant(obj)
        if not variant:
            return None
        wishlist=Wishlist.objects.filter(
            user=request.user,
            variant=variant
        ).first()
        return {
            "is_wishlisted":wishlist is not None,
            "wishlist_id":wishlist.id if wishlist else None
        }
    
    def get_primary_image(self,obj):
        variant=self.get_featured_variant(obj)
        if not variant:
            return None
        
        image=variant.product_color.images.filter(
            is_primary=True
        ).first()

        if image:
            return image.image.url
        return None
    

    def get_price(self,obj):
        variant=self.get_featured_variant(obj)
        if variant:
            return str(variant.price.amount)
        return None
        
    def get_discount_price(self,obj):
        variant=self.get_featured_variant(obj)
        if variant:
            return str(variant.discount_price.amount)
        return None

    def get_featured_variant_id(self,obj):
        variant=self.get_featured_variant(obj)
        if variant:
            return variant.id
        return None
    
    def get_is_wishlisted(self,obj):
        request=self.context.get("request")
        if (
            not request
            or
            not request.user.is_authenticated
        ):
            return False
        
        variant=self.get_featured_variant(obj)
        if not variant:
            return False
        
        return Wishlist.objects.filter(
            user=request.user,
            variant=variant
        ).exists()
        
    
    
class ProductCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model=Product
        fields=[
            "name",
            "description",
            "brand",
            "category",
            "product_type",
            "gender",
            "style",
            "is_featured",
            "is_new_arrival",
        ]

  
class ProductDetailSerializer(serializers.ModelSerializer):
    reviews=ReviewSerializer(read_only=True,many=True)
    variants=serializers.SerializerMethodField()
    rating=serializers.FloatField(read_only=True)
    product_colors=ProductColorSerializer(
        many=True,
        read_only=True
    )


    class Meta:
        model=Product
        fields = [
            "id",
            "name",
            "slug",
            "description",
            "brand",
            "category", 
            "product_type",
            "gender",
            "style",
            "is_featured",
            "is_new_arrival",
            "created_at",
            "variants",
            "product_colors",
            "reviews",
            "rating"
        ]
    def get_variants(self,obj):
        return ProductVariantSerializer(
            obj.variants.all(),
            many=True,
            context=self.context
        ).data


class ProductUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model=Product
        fields=[
            "name",
            "description",
            "brand",
            "category",
            "product_type",
            "gender",
            "style",
            "is_featured",
            "is_new_arrival"
        ]

class ProductImageUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model=ProductImage
        fields=[
            "image",
            "alt_text",
            "is_primary"
        ]

    def update(self,instance,validated_data):
        if (
            "is_primary" in validated_data and
            validated_data["is_primary"] is False and
             instance.is_primary
        ):
            raise serializers.ValidationError("Cannot unset primary image.Set another image as primary first.")
        if (
            "is_primary" in validated_data and 
            validated_data["is_primary"]
           ):
            instance.product_color.images.update(
                is_primary=False
            )
            validated_data["is_active"]=True

        return super().update(instance,validated_data)
    

    
