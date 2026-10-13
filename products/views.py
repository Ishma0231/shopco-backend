from rest_framework.generics import (ListAPIView,RetrieveAPIView,
                                     CreateAPIView,UpdateAPIView,DestroyAPIView,)
from .models import (Product,ProductVariant,ProductImage,Gender,Category,ProductColor)
from .serializers import (ProductListSerializer,ProductCreateSerializer,ProductVariantUpdateSerializer,
                          ProductDetailSerializer,ProductUpdateSerializer,ProductImageUpdateSerializer
                          ,ProductVariantCreateSerializer,ProductImageSerializer)
from rest_framework.permissions import (AllowAny,IsAdminUser,)
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import ValidationError
from rest_framework.views import APIView
from rest_framework.response import Response
from common.pagination import CustomPagination
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter,OrderingFilter
from .filters import ProductFilter
from django.db.models import Min,Avg,F,Max,Prefetch
from django.db.models.functions import Coalesce
from rest_framework import status


# Create your views here.

class ListProductsAPIView(ListAPIView):
    queryset=(Product.objects.annotate(
        rating=Avg("reviews__rating"),
        price=Min(
            Coalesce(
                F("variants__discount_price"),
                F("variants__price")
            )
        )
    )
    .prefetch_related(
        "variants__product_color__images",
        "variants__size")
        .select_related("brand",
                        "gender",
                        "product_type",
                        "category",
                        "style",
                    )
    )
    filter_backends=[DjangoFilterBackend,SearchFilter,OrderingFilter]
    search_fields=[
        "name","description",
        "brand__name","product_type__name",
        "category__name","gender__name","style__name","product_colors__color__name"]
    
    filterset_class=ProductFilter
    ordering_fields=[
        "price",
        "rating",
        "created_at"
    ]
    ordering=[
        "-created_at"
    ]
    serializer_class=ProductListSerializer
    permission_classes=[AllowAny]
    pagination_class=CustomPagination

class CreateProductAPIView(CreateAPIView):
    serializer_class=ProductCreateSerializer
    permission_classes=[IsAdminUser]

class ProductDetailAPIView(RetrieveAPIView):
    queryset=Product.objects.annotate(
        rating=Avg("reviews__rating")
    ).select_related(
        "brand","category","product_type","style","gender"
    ).prefetch_related(
        Prefetch(
            "variants",
            queryset=ProductVariant.objects
            .filter(is_active=True)
            .select_related(
                "size",
                "product_color__color"
            )
            
        ),
        Prefetch(
            "product_colors",
            queryset=ProductColor.objects.prefetch_related(
                "images"
            )
        ),

        "reviews__images"
    )
    
    lookup_field="slug"
    permission_classes=[AllowAny]
    serializer_class=ProductDetailSerializer

class ProductUpdateAPIView(UpdateAPIView):
    permission_classes=[IsAdminUser]
    queryset=Product.objects.all()
    serializer_class=ProductUpdateSerializer
    lookup_field="slug"


class ProductDeleteAPIView(DestroyAPIView):
    queryset=Product.objects.all()
    lookup_field="slug"
    permission_classes=[IsAdminUser]


class ProductVariantCreateAPIView(CreateAPIView):
    serializer_class=ProductVariantCreateSerializer
    permission_classes=[IsAdminUser]
    def perform_create(self, serializer):
        product=get_object_or_404(
            Product,
            slug=self.kwargs["slug"]
        )
        serializer.save(
            product=product
        )

class UpdateProductVariantAPIView(UpdateAPIView):
    queryset=ProductVariant.objects.all()
    permission_classes=[IsAdminUser]
    serializer_class=ProductVariantUpdateSerializer

class DeleteProductVariantAPIView(DestroyAPIView):
    queryset=ProductVariant.objects.all()
    permission_classes=[IsAdminUser]

    def perform_destroy(self, instance):
        if (
            instance.product.variants.filter(
                is_active=True
            ). count()<=1  
         ):
            raise ValidationError(
                "Product must have atleast one active variant."
            )
        instance.is_active=False
        instance.save()
        
class ProductImageCreateAPIView(CreateAPIView):
    serializer_class=ProductImageSerializer
    permission_classes=[IsAdminUser]
    def perform_create(self,serializer):
        product_color=get_object_or_404(
            ProductColor,
            pk=self.kwargs["pk"]
        )
        if serializer.validated_data.get(
            "is_primary"
        ):
            product_color.images.update(
                is_primary=False
            )
        serializer.save(
            product_color=product_color
        )

    
        
       

class UpdateProductImageAPIView(UpdateAPIView):
    queryset=ProductImage.objects.all()
    permission_classes=[IsAdminUser]
    serializer_class=(ProductImageUpdateSerializer)

       
class DeleteProductImageAPIView(DestroyAPIView):
    queryset=ProductImage.objects.all()
    permission_classes=[IsAdminUser]

    def perform_destroy(self,instance):
        if (
            instance.product_color.images.filter(is_active=True)
            .count()<=1):
               raise ValidationError("Product color must have atleast one active Image.")
        
        if instance.is_primary:
            raise ValidationError("Set another Image as primary before deleting this image.")
       
        instance.is_active=False
        instance.save()


class ActivateProductVariantAPIView(APIView):
    permission_classes=[IsAdminUser]
    def patch(self,request,pk):
        variant=get_object_or_404(
            ProductVariant,
            pk=pk
        )
        variant.is_active=True
        variant.save()
        return Response({"message":"Product Variant activated!"})
    
    

class ActivateProductImageAPIView(APIView):
    permission_classes=[IsAdminUser]
    def patch(self,request,pk):
        image=get_object_or_404(
            ProductImage,
            pk=pk
        )
        image.is_active=True
        image.save()

        return Response({"message":"Product Image activated!"})
    

class FilterOptionsAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        category = request.query_params.get("category")
        style = request.query_params.get("style")
        genders = request.query_params.get("gender")

        queryset = Product.objects.filter(
            variants__is_active=True
        )

        if genders:
            genders = genders.split(",")

        if category:
            queryset = queryset.filter(
                category__slug=category
            )

        if style:
            queryset = queryset.filter(
                style__slug=style
            )

        if genders:
            queryset = queryset.filter(
                gender__slug__in=genders
            )

        # Brands
        brands = queryset.values(
            brand_name=F("brand__name"),
            brand_slug=F("brand__slug")
        ).distinct()

        brands = [
            {
                "name": item["brand_name"],
                "slug": item["brand_slug"]
            }
            for item in brands
        ]

        # Product types
        product_types = queryset.values(
            type_name=F("product_type__name"),
            type_slug=F("product_type__slug")
        ).distinct()

        product_types = [
            {
                "name": item["type_name"],
                "slug": item["type_slug"]
            }
            for item in product_types
        ]

        # Styles
        styles = queryset.values(
            style_name=F("style__name"),
            style_slug=F("style__slug")
        ).distinct()

        styles = [
            {
                "name": item["style_name"],
                "slug": item["style_slug"]
            }
            for item in styles
        ]

       
        colors = queryset.values(
            color_id=F("product_colors__color__id"),
            color_name=F("product_colors__color__name"),
            color_slug=F("product_colors__color__slug"),
            color_hex_code=F("product_colors__color__hex_code")
        ).distinct()

        colors = [
            {
                "id": item["color_id"],
                "name": item["color_name"],
                "slug": item["color_slug"],
                "hex_code": item["color_hex_code"]
            }
            for item in colors
        ]

      
        sizes = queryset.values(
            size_name=F("variants__size__name"),
            size_slug=F("variants__size__slug")
        ).distinct()

        sizes = [
            {
                "name": item["size_name"],
                "slug": item["size_slug"]
            }
            for item in sizes
        ]

       
        price_range = queryset.aggregate(
            min_price=Min(
                Coalesce(
                    F("variants__discount_price"),
                    F("variants__price")
                )
            ),
            max_price=Max(
                Coalesce(
                    F("variants__discount_price"),
                    F("variants__price")
                )
            )
        )

       
        gender_list = []

        if style:
            gender_list = Gender.objects.values(
                "name",
                "slug"
            )

        elif category == Category.CategoryChoices.KIDS:
            gender_list = Gender.objects.filter(
                slug__in=["girls", "boys"]
            ).values(
                "name",
                "slug"
            )

        return Response(
            {
                "brands": brands,
                "colors": colors,
                "product_types": product_types,
                "styles": styles,
                "sizes": sizes,
                "gender_list": gender_list,
                "price_range": price_range
            },
            status=status.HTTP_200_OK
        )