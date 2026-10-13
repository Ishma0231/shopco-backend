from django.db import models
from django.conf import settings
from django.core.validators import (MinValueValidator,MaxValueValidator)

# Create your models here.
class Reviews(models.Model):
    product=models.ForeignKey(
        "products.Product",
        on_delete=models.CASCADE,
        related_name="reviews"
    )
    user=models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="reviews"
    )
    title=models.CharField(
        max_length=255
    )
    comment=models.TextField()
    rating=models.PositiveIntegerField(
        validators=[
            MinValueValidator(1),
            MaxValueValidator(5)
        ]
    )
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.email} - {self.product.name}"
    

class ReviewImage(models.Model):
    review=models.ForeignKey(
        Reviews,
        on_delete=models.CASCADE,
        related_name="images"
    )
    image=models.ImageField(upload_to="review_images/")
    created_at=models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.review.product.name}"