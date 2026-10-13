from rest_framework import serializers
from users.models import User

class SignupSerializer(serializers.Serializer):
    first_name=serializers.CharField(max_length=255)
    last_name=serializers.CharField(max_length=255)
    email=serializers.EmailField()
    def validate_email(self,value):
        if User.objects.filter(
            email=value
        ).exists():
            raise serializers.ValidationError(
               { "message":"An account with this email already exists."}
            )
        return value


class VerifySignupSerializer(serializers.Serializer):
    email=serializers.EmailField()
    otp=serializers.RegexField(
        regex=r"^\d{6}$",
        max_length=6,)
    
    def validate_email(self,value):
        if User.objects.filter(
            email=value
        ).exists():
            raise serializers.ValidationError({"message":"An account with this email already exists"})

        return value
    
class LoginSerializer(serializers.Serializer):
    email=serializers.EmailField()
    def validate_email(self,value):
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                {"message":"No account found with this email"}
            )

        return value
    
class VerifyLoginserializer(serializers.Serializer):
    email=serializers.EmailField()
    otp=serializers.RegexField(
        regex=r"^\d{6}$",
        max_length=6
    )
    def validate_email(self,value):
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError(
             {"message":"No account with this email exists"})
        return value
    


class ResendSignupOTPSerializer(serializers.Serializer):
    email=serializers.EmailField()

    def validate_email(self,value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                {"message":"An account with this email already exists."}
            )
        return value
        
class ResendLoginOTPSerializer(serializers.Serializer):
    email=serializers.EmailField()

    def validate_email(self,value):
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError({"message":"No account with this emial exists."})
        return value
    
class GoogleLoginSerializer(serializers.Serializer):
    id_token=serializers.CharField()
    