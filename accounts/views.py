from rest_framework.views import APIView
from rest_framework.generics import (RetrieveAPIView,UpdateAPIView)
from rest_framework.permissions import (AllowAny,IsAuthenticated)
from .serializers import (SignupSerializer,VerifySignupSerializer,
                          GoogleLoginSerializer,ResendSignupOTPSerializer,ResendLoginOTPSerializer,LoginSerializer,VerifyLoginserializer)
from rest_framework.response import Response
from rest_framework import status
from .utils import (generate_otp,save_signup_data,
                    get_signup_data,delete_signup_data,
                    generate_token,save_login_data,get_login_data,delete_login_data)

from .tasks import send_otp_email
from users.models import User
from users.serializers import (UserSerializer,MeSerializer,
                               EditProfileSerializer,ProfileImageSerializer)
from rest_framework.parsers import (MultiPartParser,FormParser)
from rest_framework.exceptions import ValidationError
from django.db import transaction
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from decouple import config
import requests
from django.core.files.base import ContentFile
import os,re
from django.core.files.storage import default_storage

# Create your views here.
class SignupAPIView(APIView):
    permission_classes=[AllowAny]

    def post(self,request):
        serializer=SignupSerializer(
            data=request.data
        )
        serializer.is_valid(raise_exception=True)
        otp=generate_otp()
        validated_data=serializer.validated_data
        email=serializer.validated_data["email"]
        save_signup_data(otp=otp,**validated_data)
        send_otp_email.delay(email,otp)
        return Response({
            "message":"OTP sent successfully."
        },status=status.HTTP_200_OK)
       
class VerifySignupAPIView(APIView):
    permission_classes=[AllowAny]
    
    @transaction.atomic
    def post(self,request):
        serializer=VerifySignupSerializer(
            data=request.data
        )
        serializer.is_valid(raise_exception=True)
        email=serializer.validated_data["email"]
        otp=serializer.validated_data["otp"]
        signup_data=get_signup_data(email)
        if signup_data is None :
            raise ValidationError(
               { "message":"OTP expired signup request not found "}
            )
        if signup_data["otp"]!=otp:
            raise ValidationError(
                {"message":"Invalid OTP"}
            )
        user=User.objects.create_user(
            first_name=signup_data["first_name"],
            last_name=signup_data["last_name"],
            email=email,
            usable_password=False
        )
        delete_signup_data(email)
        tokens=generate_token(user)
        response= Response({
            "message":"Account created successfully",
            "user":
                UserSerializer(user).data
            ,
            "access":tokens["access"]
        },status=status.HTTP_201_CREATED)
        response.set_cookie(
            key="refresh_token",
            value=tokens["refresh"],
            httponly=True,
            secure=False,
            samesite="Lax",
            max_age=7 * 24 * 60 * 60
        )
        return response

class LoginAPIView(APIView):
    permission_classes=[AllowAny]

    def post(self,request):
        serializer=LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email=serializer.validated_data["email"]
        otp=generate_otp()
        save_login_data(email=email,otp=otp)
        send_otp_email.delay(email=email,otp=otp)
        return Response({
            "message":"OTP sent successfully"
        },status=status.HTTP_200_OK)

        
class VerifyLoginAPIView(APIView):
    permission_classes=[AllowAny]

    def post(self,request):
        serializer=VerifyLoginserializer(
            data=request.data
        )
        serializer.is_valid(raise_exception=True)
        email=serializer.validated_data["email"]
        otp=serializer.validated_data["otp"]
        login_data=get_login_data(email)
        if login_data is None:
            raise ValidationError(
              {"message":"OTP expired or login request not found "}
            )
        if login_data["otp"] != otp:
            raise ValidationError({"message":"Invalid OTP"})
        user=User.objects.get(email=email)
        tokens=generate_token(user)
        delete_login_data(email)
        response= Response({
            "message":"Login successful!",
            "user":UserSerializer(user).data,
            "access":tokens["access"]
        },status=status.HTTP_200_OK
        )
        response.set_cookie(
            key="refresh_token",
            value=tokens["refresh"],
            httponly=True,
            secure=False,
            samesite="Lax",
            max_age=7 * 24 * 60 * 60
        )
        return response
    

class LogoutAPIView(APIView):
    permission_classes=[IsAuthenticated]

    def post(self,request):
        refresh_token=request.COOKIES.get("refresh_token")
        if not refresh_token:
            raise ValidationError({"message":"Refresh Token not found!"})
        try:
            refresh=RefreshToken(
                refresh_token
                )
            refresh.blacklist()
        except TokenError:
            raise ValidationError(
               { "message":"Invalid or expired refresh token."}
            )
        response= Response({
            "message":"You have been succesfully logged out!"
        })
        response.delete_cookie("refresh_token")
        return response

class RefreshTokenView(APIView):
    permission_classes=[AllowAny]

    def post(self,request):
        refresh_token=request.COOKIES.get("refresh_token")
        if not refresh_token:
            response=Response({
                "message":"Refresh token not found!"
            },status=status.HTTP_401_UNAUTHORIZED)

            response.delete_cookie("refresh_token")
            return response

        try:
            refresh=RefreshToken(refresh_token)
            access_token=str(refresh.access_token)
        except TokenError:
             response=Response({
                 "message":"Invalid or expired token"
             },status=status.HTTP_401_UNAUTHORIZED)
             response.delete_cookie("refresh_token")
             return response
        return Response({
            "access":access_token
        },status=status.HTTP_200_OK)


class MeAPIView(RetrieveAPIView):
    permission_classes=[IsAuthenticated]
    serializer_class=MeSerializer  

    def get_object(self):
        return self.request.user

class EditProfileAPIView(UpdateAPIView):
    permission_classes=[IsAuthenticated]
    serializer_class=EditProfileSerializer

    def get_object(self):
        return self.request.user
    
class EditProfileImageAPIView(UpdateAPIView):
    permission_classes=[IsAuthenticated]
    serializer_class=ProfileImageSerializer
    parser_classes=[MultiPartParser,FormParser]

    def get_object(self):
        return self.request.user
    
    def perform_update(self, serializer):
        user=self.get_object()
        old_image_path=None
        if user.profile_image:
            old_image_path=user.profile_image.name

        uploaded_file=serializer.validated_data["profile_image"]
        extension=os.path.splitext(uploaded_file.name)[1]
        base_name=user.email.replace("@","")

        if old_image_path:
            old_image_name=os.path.basename(old_image_path)
            old_image_base=os.path.splitext(old_image_name)[0]

            match=re.match(
                r"^(.*?)(?:_(\d+))?$",
                old_image_base
            )
            if match and match.group(2):
                number=int(match.group(2))+1
            else:
                number=1

            new_name=f"{base_name}_{number}"
        else:
           new_name=f"{base_name}{extension}"

        uploaded_file.name=f"{new_name}"
   
        serializer.save(profile_image=uploaded_file)
        if old_image_path:
            default_storage.delete(old_image_base)
        
    
class DeleteProfileImageAPIView(APIView):
    permission_classes=[IsAuthenticated]

    def delete(self,request):
        user=request.user
        if not user.profile_image:
            raise ValidationError({"message":"No profile image found"})
        
        user.profile_image.delete(save=False)
        user.profile_image=None
        user.save()
        return Response({
            "message":"Profile image deleted successfully!"
        },status=status.HTTP_200_OK)


class ResendSignupOTPAPIView(APIView):
    permission_classes=[AllowAny]

    def post(self,request):
        serializer=ResendSignupOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email=serializer.validated_data["email"]
        signup_data=get_signup_data(email)
        if signup_data is None:
            raise ValidationError({"message":"Invalid or expired OTP"})
        otp=generate_otp()
        save_signup_data(otp=otp,
                         email=signup_data["email"],
                         first_name=signup_data["first_name"],
                         last_name=signup_data["last_name"]
                         )
        
        send_otp_email.delay(otp=otp,email=email)
        return Response({
            "message":"OTP sent successfully."
        },status=status.HTTP_200_OK)
    
class ResendLoginOTPAPIView(APIView):
    permission_classes=[AllowAny]

    def post(self,request):
        serializer=ResendLoginOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email=serializer.validated_data["email"]
        login_data=get_login_data(email)
        if login_data is None:
            raise ValidationError("OTP expired or Invalid request")
        otp=generate_otp()
        save_login_data(email=email,otp=otp)
        send_otp_email.delay(email=email,otp=otp)
        return Response({
            "message":"OTP sent successfully"
        },status=status.HTTP_200_OK)

class GoogleLoginAPIView(APIView):
    permission_classes=[AllowAny]
    
    @transaction.atomic
    def post(self,request):
        serializer=GoogleLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        google_token=serializer.validated_data["id_token"]
        try:
            user_info=id_token.verify_oauth2_token(
                google_token,
                google_requests.Request(),
                config("GOOGLE_CLIENT_ID")
            )
            if not user_info["email_verified"]:
                 raise ValidationError({"message":"Google email is not verified."})
            
        except ValueError:
            raise ValidationError({"message":"Invalid token"})

        email=user_info["email"]
       
        user=User.objects.filter(email=email).first()
        if user:
            tokens=generate_token(user)

        else:
            user=User.objects.create_user(
                email=user_info["email"],
                first_name=user_info.get("given_name",""),
                last_name=user_info.get("family_name",""),
                usable_password=False
            )
            image_url=user_info.get("picture")
            if image_url :
                try:
                    response=requests.get(image_url)
                    response.raise_for_status()
                    image_file=ContentFile(response.content)
                    file_name=f"{user.email}.jpg"
                    user.profile_image.save(
                        file_name,
                        image_file,
                        save=True
                    )
                except requests.RequestException:
                    pass
           
            tokens=generate_token(user)
            
        response= Response({
            "message":"Google login successful.",
            "user":UserSerializer(user).data,
            "access":tokens["access"]
        },status=status.HTTP_200_OK)
        response.set_cookie(
            key="refresh_token",
            value=tokens["refresh"],
            httponly=True,
            secure=False,
            samesite="Lax",
            max_age=7 * 24 * 60 * 60
        )
        return response



