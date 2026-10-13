from rest_framework import serializers
from .models import Reviews,ReviewImage
from django.db import transaction

class ReviewImageSerializer(serializers.ModelSerializer):
    class Meta:
        model=ReviewImage
        fields=[
            "id",
            "image"
        ]


class ReviewImageBulkCreateSerializer(serializers.Serializer):
    images=serializers.ListField(
        child=serializers.ImageField(),
        required=True,
        write_only=True
    )

    def create(self, validated_data):
       review=self.context.get("review")
       images=validated_data["images"]
       for image in images:
           ReviewImage.objects.create(
               review=review,
               image=image
           )
       return review

   


class ListReviewSerializer(serializers.ModelSerializer):
    images=ReviewImageSerializer(many=True,required=False)
    user_id=serializers.IntegerField(
        source="user.id",
        read_only=True
    )
    first_name=serializers.CharField(
        source="user.first_name",
        read_only=True
    )
    last_name=serializers.CharField(
        source="user.last_name",
        read_only=True
    )
    class Meta:
        model=Reviews
        fields=[
            "id",
            "first_name",
            "last_name",
            "title",
            "comment",
            "rating",
            "user_id",
            "created_at",
            "images"
        ]

class ReviewCreateSerializer(serializers.ModelSerializer):
    images=serializers.ListField(
        child=serializers.ImageField(),
        required=False,
        write_only=True
    )
    class Meta:
        model=Reviews
        fields=[
            "title",
            "comment",
            "rating",
            "images"
        ]

    @transaction.atomic
    def create(self,validated_data):
        images=validated_data.pop("images",[])
        review=Reviews.objects.create(
            **validated_data
        )
        for image in images:
            ReviewImage.objects.create(
                review=review,
                image=image
            )
        return review

class ReviewSerializer(serializers.ModelSerializer):
    images=ReviewImageSerializer(many=True,read_only=True)
    class Meta:
        model=Reviews
        fields=[
            "id",
            "user",
            "title",
            "comment",
            "rating",
            "created_at",
            "updated_at",
            "images"
        ]

class ReviewUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model=Reviews
        fields=[
            "title",
            "comment",
            "rating"
        ]