from .models import Address,User
from rest_framework import serializers

class AddressSerializer(serializers.ModelSerializer):
    is_default=serializers.BooleanField(required=False)
    class Meta:
        model=Address
        fields=[
            "id",
            "address_type",
            "full_name",
            "phone_number",
            "street_address",
            "landmark",
            "city",
            "state",
            "country",
            "postal_code",
            "is_default"
        ]

    def create(self,validated_data):
        if (
            not validated_data["user"].addresses.exists()
        ):
            validated_data["is_default"]=True

        return Address.objects.create(**validated_data)
        
    

        
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model=User
        fields=[
            "id",
            "first_name",
            "last_name",
            "email",
            "phone_number",
            "profile_image"
        ]

class MeSerializer(serializers.ModelSerializer):
    class Meta:
        model=User
        fields=[
            "id",
            "first_name",
            "last_name",
            "email",
            "phone_number",
            "profile_image"
        ]

class EditProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model=User
        fields=[
            "first_name",
            "last_name",
            "phone_number",
           
        ]

class ProfileImageSerializer(serializers.ModelSerializer):
    class Meta:
        model=User
        fields=[
            "profile_image"
        ]