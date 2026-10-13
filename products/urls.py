from django.urls import path

from .views import (
    ListProductsAPIView,
    CreateProductAPIView,
    ProductDetailAPIView,
    ProductUpdateAPIView,
    ProductDeleteAPIView,
    ProductVariantCreateAPIView,
    UpdateProductVariantAPIView,
    DeleteProductVariantAPIView,
    ProductImageCreateAPIView,
    UpdateProductImageAPIView,
    DeleteProductImageAPIView,
    FilterOptionsAPIView,
)

from .lookup_views import (
    ListCreateBrandView,
    RetrieveUpdateDestroyBrandAPIView,
    ListCreateCategoryAPIView,
    RetrieveUpdateDestroyCategoryAPIView,
    ListCreateColorAPIView,
    RetrieveUpdateDestroyColorAPIView,
    ListCreateGenderAPIView,
    RetrieveUpdateDestroyGenderAPIView,
    ListCreateProductTypeAPIView,
    RetrieveUpdateDestroyProductTypeAPIView,
    ListCreateSizeAPIView,
    RetrieveUpdateDestroySizeAPIView,
    ListCreateStyleAPIView,
    RetrieveUpdateDestroyStyleAPIView,
    ListBrandsView,
)


urlpatterns = [

    path(
        "",
        ListProductsAPIView.as_view(),
        name="product-list",
    ),

    path(
        "filter-options/",
        FilterOptionsAPIView.as_view(),
        name="filter-options",
    ),


    path(
        "create/",
        CreateProductAPIView.as_view(),
        name="product-create",
    ),

    path(
        "brand/",
        ListCreateBrandView.as_view(),
    ),

    path(
        "brands/",
        ListBrandsView.as_view(),
    ),

    path(
        "category/",
        ListCreateCategoryAPIView.as_view(),
    ),

    path(
        "product-type/",
        ListCreateProductTypeAPIView.as_view(),
    ),

    path(
        "color/",
        ListCreateColorAPIView.as_view(),
    ),

    path(
        "gender/",
        ListCreateGenderAPIView.as_view(),
    ),

    path(
        "style/",
        ListCreateStyleAPIView.as_view(),
    ),

    path(
        "size/",
        ListCreateSizeAPIView.as_view(),
    ),


    path(
        "brand/<int:pk>/",
        RetrieveUpdateDestroyBrandAPIView.as_view(),
    ),

    path(
        "category/<int:pk>/",
        RetrieveUpdateDestroyCategoryAPIView.as_view(),
    ),

    path(
        "product-type/<int:pk>/",
        RetrieveUpdateDestroyProductTypeAPIView.as_view(),
    ),

    path(
        "gender/<int:pk>/",
        RetrieveUpdateDestroyGenderAPIView.as_view(),
    ),

    path(
        "color/<int:pk>/",
        RetrieveUpdateDestroyColorAPIView.as_view(),
    ),

    path(
        "size/<int:pk>/",
        RetrieveUpdateDestroySizeAPIView.as_view(),
    ),

    path(
        "style/<int:pk>/",
        RetrieveUpdateDestroyStyleAPIView.as_view(),
    ),

    path(
        "variant/<int:pk>/update/",
        UpdateProductVariantAPIView.as_view(),
    ),

    path(
        "variants/<int:pk>/delete/",
        DeleteProductVariantAPIView.as_view(),
    ),

    path(
        "images/<int:pk>/update/",
        UpdateProductImageAPIView.as_view(),
    ),

    path(
        "images/<int:pk>/delete/",
        DeleteProductImageAPIView.as_view(),
    ),

    path(
        "<slug:slug>/",
        ProductDetailAPIView.as_view(),
        name="product-detail",
    ),

    path(
        "<slug:slug>/update/",
        ProductUpdateAPIView.as_view(),
        name="product-update",
    ),

    path(
        "<slug:slug>/delete/",
        ProductDeleteAPIView.as_view(),
        name="product-delete",
    ),

    path(
        "<slug:slug>/variants/create/",
        ProductVariantCreateAPIView.as_view(),
        name="variant-create",
    ),

    path(
        "<slug:slug>/images/create/",
        ProductImageCreateAPIView.as_view(),
        name="image-create",
    ),
]