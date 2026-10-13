from django.db import models
from django.contrib.auth.models import (AbstractUser,
                                        BaseUserManager)
from phonenumber_field.modelfields import PhoneNumberField
from django_countries.fields import CountryField
from django.core.validators import RegexValidator
from accounts.tasks import send_welcome_email
class UserManager(BaseUserManager):
    def create_user(self,email,password=None,usable_password=True,**extra_fields):
        if not email:
            raise ValueError("Email Required")
        email=self.normalize_email(email)
        user=self.model(email=email,**extra_fields)
        if usable_password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save(using=self._db)
        send_welcome_email.delay(email=email,first_name=user.first_name)
        return user
    
    def create_superuser(self,email,password=None,**extra_fields):
        extra_fields.setdefault("is_staff",True)
        extra_fields.setdefault("is_superuser",True)
        return self.create_user(email,password,**extra_fields)
  
# Create your models here.
class User(AbstractUser):
    objects=UserManager()
    username=None
    email=models.EmailField(unique=True)
    phone_number=PhoneNumberField(blank=True,null=True)
    profile_image=models.ImageField(
        upload_to="profiles/",
        blank=True,
        null=True
    )
    updated_at=models.DateTimeField(auto_now=True)
    USERNAME_FIELD="email"
    REQUIRED_FIELDS=[]

    def __str__(self):
        return self.email


class Address(models.Model):
    class AddressType(models.TextChoices):
        HOME="home","Home"
        OFFICE="office","Office"

    user=models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="addresses"
    )
    address_type=models.CharField(
        choices=AddressType.choices,
        max_length=20
    )
    full_name=models.CharField(
        max_length=255
    )
    phone_number=PhoneNumberField()

    street_address=models.CharField(
        max_length=255
    )
    landmark=models.CharField(
        max_length=255,
        blank=True
    )
    city=models.CharField(
        max_length=100
    )
    state=models.CharField(max_length=100)
    country=CountryField()
    postal_code=models.CharField(
        max_length=6,
        validators=[RegexValidator(
            regex=r"^[1-9][0-9]{5}",
            message="Enter a valid Indian PIN code."
        )]
                                 )
    is_default=models.BooleanField(default=False)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.email} - {self.address_type}"
