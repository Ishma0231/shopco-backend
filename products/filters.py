import django_filters
from .models import Product

class ProductFilter(django_filters.FilterSet):
    brand=django_filters.CharFilter(
        method="filter_multiple"
    )
    style=django_filters.CharFilter(
        method="filter_multiple"
    )
    category=django_filters.CharFilter(
       method="filter_multiple"
    )
    product_type=django_filters.CharFilter(
       method="filter_multiple"
    )
    gender=django_filters.CharFilter(
        method="filter_multiple"
    )
    color=django_filters.CharFilter(
        method="filter_variant_multiple"
    )
    size=django_filters.CharFilter(
        method="filter_variant_multiple"

    )
    min_price=django_filters.NumberFilter(
        field_name="variants__price",
        lookup_expr="gte"
    )
    max_price=django_filters.NumberFilter(
        field_name="variants__price",
        lookup_expr="lte"
    )

    is_featured=django_filters.BooleanFilter(
        field_name="is_featured",
        lookup_expr="exact"
    )

    is_new_arrival=django_filters.BooleanFilter(
        field_name="is_new_arrival",
        lookup_expr="exact"
    )

    def filter_multiple(self,queryset,name,value):
        values=value.split(",")
        return queryset.filter(
            **{f"{name}__slug__in":values}
            )

    def filter_variant_multiple(self,queryset,name,value):
        values=value.split(",")

        if name=="color":
            return queryset.filter(
               product_colors__color__slug__in=values
            ).distinct()
        return queryset.filter(**{
            f"variants__{name}__slug__in":values
        }).distinct()

    class Meta:
        model=Product
        fields=[]