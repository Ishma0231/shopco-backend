from django.db import models
from django.conf import settings

# Create your models here.
class Cart(models.Model):
    user=models.OneToOneField(
        settings.AUTH_USER_MODEL,
        related_name="cart",
        on_delete=models.CASCADE,
    )
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.email
    
class CartItem(models.Model):
    cart=models.ForeignKey(
        Cart,
        related_name="items",
        on_delete=models.CASCADE
    )
    variant=models.ForeignKey(
        "products.ProductVariant",
        on_delete=models.CASCADE,
        related_name="cart_items"
    )

    quantity=models.PositiveIntegerField(default=1)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)


    def __str__(self):
        return f"{self.variant.product.name} x {self.quantity}"

