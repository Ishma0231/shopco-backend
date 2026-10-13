from rest_framework.generics import (ListAPIView,ListCreateAPIView,RetrieveUpdateDestroyAPIView)
from .serializers import (BrandSerializer,StyleSerializer,
                          CategorySerializer,SizeSerializer,ColorSerializer,
                          ProductTypeSerializer,GenderSerializer)
from .models import (Brand,Style,Size,Color,ProductType,Category,Gender)
from rest_framework.permissions import (IsAdminUser,AllowAny)

class ListCreateBrandView(ListCreateAPIView):
    permission_classes=[IsAdminUser]
    queryset=Brand.objects.all()
    serializer_class=BrandSerializer

class ListBrandsView(ListAPIView):
    permission_classes=[AllowAny]
    queryset=Brand.objects.all()
    serializer_class=BrandSerializer

class RetrieveUpdateDestroyBrandAPIView(RetrieveUpdateDestroyAPIView):
    permission_classes=[IsAdminUser]
    queryset=Brand.objects.all()
    serializer_class=BrandSerializer

class ListCreateCategoryAPIView(ListCreateAPIView):
    permission_classes = [IsAdminUser]
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class RetrieveUpdateDestroyCategoryAPIView(RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAdminUser]
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class ListCreateProductTypeAPIView(ListCreateAPIView):
    permission_classes = [IsAdminUser]
    queryset = ProductType.objects.all()
    serializer_class = ProductTypeSerializer


class RetrieveUpdateDestroyProductTypeAPIView(RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAdminUser]
    queryset = ProductType.objects.all()
    serializer_class = ProductTypeSerializer


class ListCreateGenderAPIView(ListCreateAPIView):
    permission_classes = [IsAdminUser]
    queryset = Gender.objects.all()
    serializer_class = GenderSerializer


class RetrieveUpdateDestroyGenderAPIView(RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAdminUser]
    queryset = Gender.objects.all()
    serializer_class = GenderSerializer


class ListCreateColorAPIView(ListCreateAPIView):
    permission_classes = [IsAdminUser]
    queryset = Color.objects.all()
    serializer_class = ColorSerializer


class RetrieveUpdateDestroyColorAPIView(RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAdminUser]
    queryset = Color.objects.all()
    serializer_class = ColorSerializer


class ListCreateSizeAPIView(ListCreateAPIView):
    permission_classes = [IsAdminUser]
    queryset = Size.objects.all()
    serializer_class = SizeSerializer


class RetrieveUpdateDestroySizeAPIView(RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAdminUser]
    queryset = Size.objects.all()
    serializer_class = SizeSerializer


class ListCreateStyleAPIView(ListCreateAPIView):
    permission_classes = [IsAdminUser]
    queryset = Style.objects.all()
    serializer_class = StyleSerializer


class ListCreateStyleAPIView(ListCreateAPIView):
    queryset = Style.objects.all()
    serializer_class = StyleSerializer

    def get_permissions(self):
        if self.request.method in ["GET", "HEAD", "OPTIONS"]:
            return [AllowAny()]

        return [IsAdminUser()]
    

class RetrieveUpdateDestroyStyleAPIView(RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAdminUser]
    queryset = Style.objects.all()
    serializer_class = StyleSerializer