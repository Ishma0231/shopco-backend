from django.contrib import admin
from .models import (Category,Brand,ProductType,Gender,Color,
                     Size,Style,Product,ProductImage,ProductVariant,ProductColor)
# Register your models here.
admin.site.register([Category,Brand,ProductType,Gender,Color,
                     Size,Style,Product,ProductImage,ProductColor,ProductVariant])