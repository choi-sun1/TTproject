from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.views import APIView
from .models import User
from .serializers import SignupSerializer, UserProfileSerializer, UserUpdateSerializer 
from django.core.cache import cache
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from django.http import JsonResponse



class SignupView(APIView):
    '''회원가입'''
    authentication_classes = [] # 인증 설정 무시
    permission_classes = []     # 권한 없이 누구나 접근 가능
    
    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'message': '회원가입이 완료되었습니다.'
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class LoginView(APIView):
    '''로그인'''
    authentication_classes = [] # 인증 설정 무시
    permission_classes = []     # 권한 없이 누구나 접근 가능
    
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        user = User.objects.filter(email=email).first()
        
        # 사용자  인증
        user = authenticate(request, email=email, password=password)
        if user is not None:
            # JWT 토큰 생성
            refresh = RefreshToken.for_user(user)
            return JsonResponse({
                'access': str(refresh.access_token),
                'refresh': str(refresh),
                'message': '로그인 성공'
            }, status=200)
        else:
            return JsonResponse({'error': '사용자명 또는 비밀번호가 올바르지 않습니다.'}, status=400)
        

class LogoutView(APIView):
    '''로그아웃'''
    permission_classes = [IsAuthenticated] # 인증된 사용자만 접근 가능
    
    def post(self, request):
        try:
            refresh_token = request.data['refresh']
            token = RefreshToken(refresh_token)
            token.blacklist() # 토큰 블랙리스트 추가
            return Response({'message': '로그아웃 성공'}, status=200)
        except Exception as e:
            return Response({'error': '로그아웃 실패'}, status=400)
        
class UserProfile(APIView):
    '''유저 프로필 조회'''
    permission_classes = [IsAuthenticated] # 인증된 사용자만 접근 가능
    
    def get(self, request):
        user = request.user
        serializer = UserProfileSerializer(user)
        return Response(serializer.data)
    
    def put(self, request):
        user = request.user
        serializer = UserUpdateSerializer(user, data=request.data, partial=True)
        if not any(field in serializer.validated_data for field in serializer.fields):
            return Response({
                'message': '이 정보는 수정할 수 없습니다.'
            }, status=status.HTTP_400_BAD_REQUEST)

        if serializer.is_valid():
            serializer.save()
            return Response({
                'message': '회원정보가 성공적으로 수정되었습니다.',
                'user': serializer.data
            }, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
