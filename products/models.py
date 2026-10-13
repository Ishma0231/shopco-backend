from django.db import models
from django.conf import settings
import uuid
from django.utils.text import slugify
from django.core.exceptions import ValidationError
from djmoney.models.fields import MoneyField
# Create your models here.
class Category(models.Model):
    class CategoryChoices(models.TextChoices):
        MEN="men","Men"
        WOMEN="women","Women"
        KIDS="kids","Kids"

    name=models.CharField(max_length=100,unique=True,
                          choices=CategoryChoices.choices
                          )
    slug=models.SlugField(unique=True,blank=True)

    def save(self,*args,**kwargs):
        self.slug=slugify(self.name)
        super().save(*args,**kwargs)

    def __str__(self):
        return self.name
    
class Brand(models.Model):
    name=models.CharField(max_length=100,unique=True)
    slug=models.SlugField(unique=True,blank=True)
  
    def save(self,*args,**kwargs):
        self.slug=slugify(self.name)
        super().save(*args,**kwargs)

    def __str__(self):
        return self.name
    
class ProductType(models.Model):
    name=models.CharField(max_length=100,unique=True)
    slug=models.SlugField(unique=True,blank=True)

    def save(self,*args,**kwargs):
        self.slug=slugify(self.name)
        super().save(*args,**kwargs)


    def __str__(self):
        return self.name

class Gender(models.Model):
    name=models.CharField(max_length=100,unique=True)
    slug=models.SlugField(unique=True,blank=True)

    def save(self,*args,**kwargs):
        self.slug=slugify(self.name)
        super().save(*args,**kwargs)


    def __str__(self):
        return self.name


class Color(models.Model):
    name=models.CharField(max_length=100,unique=True)
    slug=models.SlugField(unique=True,blank=True)
    hex_code = models.CharField(max_length=7)

    def save(self,*args,**kwargs):
        self.slug=slugify(self.name)
        super().save(*args,**kwargs)


    def __str__(self):
        return self.name

class Size(models.Model):
    name=models.CharField(max_length=100,unique=True)
    slug=models.SlugField(unique=True,blank=True)

    def save(self,*args,**kwargs):
        self.slug=slugify(self.name)
        super().save(*args,**kwargs)


    def __str__(self):
        return self.name

class Style(models.Model):
    name=models.CharField(max_length=100,unique=True)
    slug=models.SlugField(unique=True,blank=True)

    def save(self,*args,**kwargs):
        self.slug=slugify(self.name)
        super().save(*args,**kwargs)

    def __str__(self):
        return self.name
    
class Product(models.Model):
    name=models.CharField(max_length=255)
    slug=models.SlugField(unique=True,blank=True)
    description=models.TextField()
    brand=models.ForeignKey(
        Brand,
        on_delete=models.CASCADE,
        related_name="products"
        )
    category=models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="products"
    )
    product_type=models.ForeignKey(
        ProductType,
        on_delete=models.CASCADE,
        related_name="products"
    )
    gender=models.ForeignKey(
        Gender,
        on_delete=models.CASCADE,
        related_name="products"
    )
    style=models.ForeignKey(
        Style,
        on_delete=models.CASCADE,
        related_name="products"
    )
    
    is_featured=models.BooleanField(default=False)
    is_new_arrival=models.BooleanField(default=False)
    created_at=models.DateTimeField(auto_now_add=True)

    def save(self,*args,**kwargs):
        if not self.slug:
            self.slug=(
                f"{slugify(self.name)}"
                f"-{uuid.uuid4().hex[:5]}")
            
        super().save(*args,**kwargs)  

    def __str__(self):
        return self.name


class ProductColor(models.Model):
    product=models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="product_colors"
    )
    color=models.ForeignKey(
        Color,
        on_delete=models.CASCADE,
    )
    class Meta:
        unique_together=("product","color")

    def __str__(self):
       return f"{self.product.name}-{self.color.name}"

class ProductVariant(models.Model):
    product=models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="variants"
    )
    product_color=models.ForeignKey(
        ProductColor,
        on_delete=models.CASCADE,
        related_name="variants"
    )
    size=models.ForeignKey(
        Size,
        on_delete=models.CASCADE,
       
    )
    stock=models.PositiveIntegerField(
        default=0
    )
    price=MoneyField(
            max_digits=10,        
            decimal_places=2,
            default_currency="INR"
    )
    discount_price=MoneyField(
            max_digits=10,        
            decimal_places=2,
            default_currency="INR",
            blank=True,
            null=True
    )
    sku=models.CharField(
        max_length=100,
        unique=True,
        blank=True
    )
    is_active=models.BooleanField(default=True)
    min_order_quantity=models.PositiveIntegerField(default=1)
    estimated_delivery_days=models.PositiveIntegerField(default=5)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)

    class Meta:
        unique_together=("product_color","size")

    def save(self,*args,**kwargs):
        if self.pk:
            old=ProductVariant.objects.get(pk=self.pk)
            if (
                old.is_active
                and
                not self.is_active
            ):
                active_count=old.product.variants.filter(
                    is_active=True
                ).count()

                if active_count<=1:
                    raise ValidationError("Product must have atleast one active variant")
                
        else:
            variant_count=ProductVariant.objects.count()
            if ( 
                variant_count == 0 and
                not self.is_active
                ):
                raise ValidationError("First variant must be active")

        if not self.sku:
                self.sku=(
                    f"{self.product.name[:3]}"
                    f"-{self.product_color.color.name[:3]}"
                    f"-{self.size.name}"
                    f"-{uuid.uuid4().hex[:4]}"
                ).upper()
        
        super().save(*args,**kwargs)
        

    def delete(self,*args,**kwargs):
        self.is_active=False
        self.save()


    def __str__(self):
        return f"{self.sku}"


class ProductImage(models.Model):
    product_color = models.ForeignKey(
            ProductColor,
            related_name="images",
            on_delete=models.CASCADE
        )
    image=models.ImageField(upload_to="products/")
    alt_text=models.CharField(max_length=100,blank=True)
    is_primary=models.BooleanField(default=False)
    is_active=models.BooleanField(default=True)

    
    def save(self,*args,**kwargs):
        if self.pk:
            old=ProductImage.objects.get(
                pk=self.pk
            )
            if (
                old.is_primary and
                not self.is_primary
            ):
                raise ValidationError("Cannot unset a primary image")
            if (
                 old.is_primary and
                 old.is_active and
                 not self.is_active
            ):
                raise ValidationError("Primary image cannot be deactivated")
            
               
            if (
                old.is_active and
                not self.is_active
            ):
                active_count=self.product_color.images.filter(
                    is_active=True
                ).count()
                if active_count <= 1:
                    raise ValidationError("Product color must have atleast one active image")
        else:
            image_count=self.product_color.images.count()
            if (
                image_count == 0 
            ):
                if (
                    not self.is_primary
                    or not self.is_active):
                    raise ValidationError("First image must be primary and active")
                
        if self.is_primary:
                self.is_active=True
                self.product_color.images.exclude(
                    pk=self.pk
                ).update(is_primary=False)

                
        super().save(*args,**kwargs)
    
    def delete(self,*args,**kwargs):
        if self.is_primary:
            raise ValidationError("Set another as primary before deleting this one.")
        self.is_active=False
        self.save()

    def __str__(self):
        return f"{self.product_color.product.name}-{self.product_color.color.name}"

