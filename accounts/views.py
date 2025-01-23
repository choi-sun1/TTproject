from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly, AllowAny
from rest_framework.views import APIView
from .models import User, RelatedModel
from .serializers import SignupSerializer, UserProfileSerializer, UserUpdateSerializer, UserSerializer, RegisterSerializer
from django.core.cache import cache
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken, UntypedToken
from django.http import JsonResponse
from articles.models import Article
from rest_framework.decorators import api_view
from .forms import UserCreationForm, UserChangeForm
from django.contrib.auth import get_user_model
from django.contrib.auth.views import PasswordResetView
from django.urls import reverse_lazy
from django.contrib import messages
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from .serializers import (
    UserSerializer, RegisterSerializer, UserProfileSerializer,
    UserUpdateSerializer, UserDetailSerializer
)

User = get_user_model()

class RegisterAPIView(generics.CreateAPIView):
    """
    사용자 회원가입 API
    
    Request Body:
        - email: 이메일 주소 (필수)
        - password: 비밀번호 (필수)
        - password2: 비밀번호 확인 (필수)
        - nickname: 닉네임 (필수)
        - birth_date: 생년월일 (선택, YYYY-MM-DD)
        - gender: 성별 (선택, 'M' 또는 'F')
    """
    queryset = User.objects.all()
    permission_classes = (permissions.AllowAny,)
    serializer_class = RegisterSerializer

class ProfileAPIView(generics.RetrieveAPIView):
    """
    사용자 프로필 조회 API
    
    Response:
        - email: 이메일 주소
        - nickname: 닉네임
        - profile_image: 프로필 이미지 URL
        - birth_date: 생년월일
        - gender: 성별
        - articles_count: 작성 게시글 수
        - itineraries_count: 작성 일정 수
    """
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = UserProfileSerializer

    def get_object(self):
        return self.request.user

class ProfileUpdateAPIView(generics.UpdateAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = UserUpdateSerializer

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

class SignupView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (permissions.AllowAny,)
    serializer_class = RegisterSerializer

class LoginView(APIView):
    permission_classes = (permissions.AllowAny,)
    
    def post(self, request):
        # JWT 인증 처리는 rest_framework_simplejwt가 처리
        pass

class LogoutView(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    
    def post(self, request):
        # JWT 토큰 무효화 로직
        return Response(status=status.HTTP_200_OK)

class UserProfileView(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserDetailSerializer
    lookup_field = 'nickname'
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

def profile_view(request):
    # 템플릿 뷰 구현
    pass

def profile_edit(request):
    # 템플릿 뷰 구현
    pass