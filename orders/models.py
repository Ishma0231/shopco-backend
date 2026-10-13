from django.db import models
from django.conf import settings
import uuid
from users.models import Address
from phonenumber_field.modelfields import PhoneNumberField
from django_countries.fields import CountryField
from djmoney.models.fields import MoneyField
from .validators import validate_future_date,validate_indian_pin

class Order(models.Model):

    class PaymentMethod(models.TextChoices):

        COD = "cod", "Cash On Delivery"
        RAZORPAY="razorpay","RazorPay"


    class PaymentStatus(models.TextChoices):

        PENDING = "pending", "Pending"

        PAID = "paid", "Paid"

        FAILED = "failed", "Failed"

        REFUNDED = "refunded", "Refunded"

        PARTIALLY_REFUNDED = (
            "partially_refunded",
            "Partially Refunded"
        )


    class OrderStatus(models.TextChoices):

       PENDING="pending","Pending"
       DELIVERED="delivered","Delivered"
       PROCESSING="processing","Processing"
       CANCELLED="cancelled","Cancelled"
       SHIPPED="shipped","Shipped"


    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="orders"
    )

    order_id=models.CharField(
        max_length=50,
        unique=True,
        blank=True
    )

    full_name = models.CharField(
        max_length=255
    )

    phone_number = PhoneNumberField()

    street_address = models.CharField(
        max_length=255
    )

    address_type=models.CharField(
        choices=Address.AddressType.choices,
        max_length=20
    )

    landmark = models.CharField(
        max_length=255,
        blank=True
    )

    city = models.CharField(
        max_length=100
    )

    state = models.CharField(
        max_length=100
    )

    country =CountryField()

    postal_code = models.CharField(
        max_length=6,
        validators=[validate_indian_pin]
    )

    payment_method = models.CharField(
        max_length=20,
        choices=PaymentMethod.choices
    )

    payment_status = models.CharField(
        max_length=30,
        choices=PaymentStatus.choices,
        default=PaymentStatus.PENDING
    )

    order_status = models.CharField(
        max_length=20,
        choices=OrderStatus.choices,
        default=OrderStatus.PENDING
    )

    total_price =MoneyField(
            max_digits=10,        
            decimal_places=2,
            default_currency="INR"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def save(self,*args,**kwargs):
        if not self.order_id:
            self.order_id=(
                f"ELR-{uuid.uuid4().hex[:12]}"
            ).upper()
        super().save(*args,**kwargs)

    def __str__(self):

        return f"{self.order_id}"
    
class OrderItem(models.Model):
    class ItemStatus(models.TextChoices):
        
        PENDING = "pending", "Pending"
        PROCESSING = "processing", "Processing"
        SHIPPED = "shipped", "Shipped"
        DELIVERED = "delivered", "Delivered"
        CANCELLED = "cancelled", "Cancelled"
        
    
    order=models.ForeignKey(
        Order,
        related_name="items",
        on_delete=models.CASCADE

    )
    variant=models.ForeignKey(
        "products.ProductVariant",
        on_delete=models.PROTECT,
        related_name="order_items"

    )
    product_name = models.CharField(
         max_length=255
    )

    color_name = models.CharField(
        max_length=100
    )

    size_name = models.CharField(
        max_length=100
    )

    price=MoneyField(
            max_digits=10,        
            decimal_places=2,
            default_currency="INR"
    )
    quantity=models.PositiveIntegerField()
    product_image=models.CharField(
       max_length=500
    )

    item_status=models.CharField(
        max_length=20,
        choices=ItemStatus.choices,
        default=ItemStatus.PENDING
    )
    estimated_delivery_date=models.DateField(
        validators=[validate_future_date]
    )
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)

    def __str__(self):     
            return f"{self.product_name} x {self.quantity}"     
                                                             