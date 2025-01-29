from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from ..serializers import (
    UserSerializer, RegisterSerializer, UserProfileSerializer,
    UserUpdateSerializer, UserDetailSerializer
)
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()

class RegisterAPIView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (permissions.AllowAny,)
    serializer_class = RegisterSerializer

class LoginAPIView(APIView):
    permission_classes = (permissions.AllowAny,)
    
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        user = authenticate(email=email, password=password)

        if user:
            token = RefreshToken.for_user(user)
            return Response({
                'user': UserSerializer(user).data,
                'token': {
                    'refresh': str(token),
                    'access': str(token.access_token),
                }
            })
        return Response(
            {'error': '이메일 또는 비밀번호가 잘못되었습니다.'},
            status=status.HTTP_401_UNAUTHORIZED
        )

class ProfileAPIView(generics.RetrieveAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = UserProfileSerializer

    def get_object(self):
        return self.request.user

class ProfileUpdateAPIView(generics.UpdateAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = UserUpdateSerializer

    def get_object(self):
        return self.request.user

class UserProfileDetailAPIView(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserDetailSerializer
    lookup_field = 'nickname'
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
