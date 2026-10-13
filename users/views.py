from rest_framework.generics import (CreateAPIView,ListAPIView,
                                     UpdateAPIView,DestroyAPIView)
from rest_framework.permissions import (IsAuthenticated)
from .serializers import AddressSerializer
from .models import Address
from django.core.exceptions import ValidationError

class CreateAddressAPIView(CreateAPIView):
    permission_classes=[IsAuthenticated]
    serializer_class=AddressSerializer

    def perform_create(self, serializer):
        user=self.request.user
        if serializer.validated_data.get(
            "is_default"
        ):
            user.addresses.update(
                is_default=False
            )
            
        serializer.save(
            user=user
        )

class EditAddressAPIView(UpdateAPIView):
    permission_classes=[IsAuthenticated]
    serializer_class=AddressSerializer

    def get_queryset(self):
        return Address.objects.filter(
            user=self.request.user
        )
    def perform_update(self, serializer):
        user=self.request.user
        instance=serializer.instance
     
        if "is_default" in serializer.validated_data:
            new_is_default=serializer.validated_data["is_default"]
            if (
                instance.is_default and
                not new_is_default
             ):
                raise ValidationError({"message":"Cannot unset a default Address"})
                

            if(
                new_is_default
            ):
                 user.addresses.exclude(
                     pk=instance.pk
                 ).update(
                        is_default=False
                        )
            
        serializer.save()

class ViewAddressAPIView(ListAPIView):
    permission_classes=[IsAuthenticated]
    serializer_class=AddressSerializer

    def get_queryset(self):
        return Address.objects.filter(
            user=self.request.user
        )

class DeleteAddressAPIView(DestroyAPIView):
    permission_classes=[IsAuthenticated]

    def get_queryset(self):
       return Address.objects.filter(
            user=self.request.user
        )
    
    def perform_destroy(self, instance):
        if instance.is_default:
            raise ValidationError({"message":"Set another address as default before deleting this one."})
        instance.delete()
    

        

    
