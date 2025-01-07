from rest_framework_simplejwt.exceptions import TokenError
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.views import APIView
from .models import User, RelatedModel
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
        serializer = SignupSerializer(data=request.data) # 시리얼라이저 인스턴스 생성
        # 시리얼라이저 유효성 검사
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
        # 요청 데이터에서 이메일과 비밀번호 가져오기
        email = request.data.get('email')
        password = request.data.get('password')
        # 사용자  인증
        user = authenticate(request, email=email, password=password)
        # 사용자가 존재하면 JWT 토큰 생성
        if user is not None:
            refresh = RefreshToken.for_user(user)
            return JsonResponse({
                'access': str(refresh.access_token),
                'refresh': str(refresh),
                'message': '로그인 성공'
            }, status=200)
        else:
            return JsonResponse({'error': '로그인 실패: 이메일 또는 비밀번호가 잘못되었습니다. 다시 시도해 주세요.'}, status=400)


class LogoutView(APIView):
    '''로그아웃'''
    authentication_classes = [IsAuthenticated] # 인증된 사용자만 접근 가능
    permission_classes = [IsAuthenticated] # 인증된 사용자만 접근 가능
    
    def post(self, request):
        # 요청 데이터에서 refresh 토큰 가져오기
        try:
            refresh_token = request.data.get('refresh')
            token = RefreshToken(refresh_token)
            token.blacklist() # 토큰 블랙리스트 추가
            return Response({'message': '로그아웃 성공'}, status=200)
        except KeyError:
            return Response({'error': 'refresh 토큰이 제공되지 않았습니다.'}, status=400)
        except TokenError:
            return Response({'error': '유효하지 않은 토큰입니다.'}, status=400)
        

class UserProfileView(APIView):
    '''유저 프로필 조회'''
    permission_classes = [IsAuthenticated] # 인증된 사용자만 접근 가능
    
    def get(self, request):
        user = request.user
        serializer = UserProfileSerializer(user)
        return Response(serializer.data)
    
    def put(self, request):
        user = request.user
        serializer = UserUpdateSerializer(user, data=request.data, partial=True)

        if serializer.is_valid():
            # 수정할 데이터가 없는 경우
            if not any(field in serializer.validated_data for field in serializer.fields):
                return Response({
                    'message': '이 정보는 수정할 수 없습니다.'
                }, status=status.HTTP_400_BAD_REQUEST)
        
            serializer.save()
            return Response({
                'message': '회원정보가 성공적으로 수정되었습니다.',
                'user': serializer.data
            }, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserDeleteView(APIView):
    '''회원탈퇴'''
    authentication_classes = [IsAuthenticated] # 인증된 사용자만 접근 가능
    permission_classes = [IsAuthenticated] # 인증된 사용자만 접근 가능
    
    def post(self, request):
        # user와 관련된 다른 모델의 데이터를 삭제하거나 업데이트
        related_data = RelatedModel.objects.filter(user=request.user)
        related_data.delete()
        
        user = request.user
        user.delete()
        return Response({'message': '회원탈퇴가 완료되었습니다.'}, status=status.HTTP_200_OK)