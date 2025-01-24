from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.shortcuts import get_object_or_404, redirect
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
from articles.models import Article
# 소셜 로그인 
from django.conf import settings
from .models import User
from allauth.socialaccount.models import SocialAccount
import os
from django.shortcuts import redirect
from dj_rest_auth.registration.views import SocialLoginView
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.kakao.views import KakaoOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import RedirectView
import requests
from json.decoder import JSONDecodeError
from allauth.socialaccount.providers.google import views as google_view
from allauth.socialaccount.providers.kakao import views as kakao_view


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
            return JsonResponse({'error': '로그인 실패: 이메일 또는 비밀번호가 잘못되었습니다. 다시 시도해 주세요.'}, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(APIView):
    '''로그아웃'''
    authentication_classes = [] 
    permission_classes = [] 
    
    def post(self, request):
        # 요청 데이터에서 refresh 토큰 가져오기
        try:
            refresh_token = request.data.get('refresh')
            token = RefreshToken(refresh_token)
            token.blacklist() # 토큰 블랙리스트 추가
            return Response({'message': '로그아웃 성공'}, status=status.HTTP_200_OK)
        except KeyError:
            return Response({'error': 'refresh 토큰이 제공되지 않았습니다.'}, status=status.HTTP_400_BAD_REQUEST)
        except TokenError:
            return Response({'error': '유효하지 않은 토큰입니다.'}, status=status.HTTP_400_BAD_REQUEST)
        

class UserProfileView(APIView):
    '''유저 프로필 조회'''
    authentication_classes = [JWTAuthentication] # JWT 토큰 인증    
    
    def get(self, request, username):
        user = get_object_or_404(User, username=username)
        serializer = UserProfileSerializer(user, context={'request':request})
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    '''유저 프로필 수정'''
    def put(self, request, username):
        user = get_object_or_404(User, username=username)
        serializer = UserUpdateSerializer(user, data=request.data, partial=True)

        if serializer.is_valid():
            # 수정할 데이터가 없으면 에러 발생
            if not any(field in serializer.validated_data for field in serializer.fields):
                return Response({
                    'message': '이 정보는 수정할 수 없습니다.'
                }, status=status.HTTP_400_BAD_REQUEST)
        
            serializer.save(raise_exception=True)
            return Response({
                'message': '회원정보가 성공적으로 수정되었습니다.',
                'user': serializer.data
            }, status=status.HTTP_200_OK)

class UserDeleteView(APIView):
    '''회원탈퇴'''
    authentication_classes = [JWTAuthentication] # JWT 인증 클래스 사용

    def delete(self, request, username):
        # user와 관련된 다른 모델의 데이터를 삭제하거나 업데이트
        user = get_object_or_404(User, username=username)
        related_data = RelatedModel.objects.filter(user=request.user)
        related_data.delete()
        
        user = request.user
        user.delete()
        return Response({'message': '회원탈퇴가 완료되었습니다.'}, status=status.HTTP_200_OK)
    

# 소셜 로그인 변수 설정
state = getattr(settings, 'STATE')
BASE_URL = 'http://localhost:8000/'
GOOGLE_CALLBACK_URI = BASE_URL + 'api/accounts/google/callback/'
KAKAO_CALLBACK_URI = BASE_URL + 'api/accounts/kakao/callback/'


# 구글 소셜 로그인
class GoogleLoginView(APIView):
    '''코드 요청'''
    def get(self, request):
        scope = "https://www.googleapis.com/auth/userinfo.email"
        client_id = getattr(settings, 'GOOGLE_CLIENT_ID')
        return redirect(f"https://accounts.google.com/o/oauth2/v2/auth?client_id={client_id}&response_type=code&redirect_uri={GOOGLE_CALLBACK_URI}&scope={scope}")

class GoogleCallbackView(APIView):
    '''콜백'''
    def get(self, request):
        client_id = getattr(settings, 'GOOGLE_CLIENT_ID')
        client_secret = getattr(settings, 'GOOGLE_SECRET')
        code = request.GET.get('code')
    
        # 액세스토큰 요청
        token_request = requests.post(
            f"https://oauth2.googleapis.com/token?client_id={client_id}&client_secret={client_secret}&code={code}&grant_type=authorization_code&redirect_uri={GOOGLE_CALLBACK_URI}&state={state}"
        )
        # json 형태로 변환 & 에러 처리
        token_request_json = token_request.json()
        error = token_request_json.get("error")

        # 에러 발생시 에러 메시지 반환
        if error is not None:
            return JsonResponse({'error': error}, status=status.HTTP_400_BAD_REQUEST)
        # 성공시 액세스 토큰 반환
        access_token = token_request_json.get("access_token")

        # 액세스 토큰으로 이메일 요청
        email_request = requests.get(f"https://www.googleapis.com/oauth2/v1/tokeninfo?access_token={access_token}")
        email_request_status = email_request.status_code

        # 이메일 요청 실패시 에러 메시지 반환
        if email_request_status != 200:
            return JsonResponse({'error': '이메일을 가져오는데 실패했습니다.'}, status=status.HTTP_400_BAD_REQUEST)
        
        # 이메일 요청 성공시 json 형태로 변환
        email_request_json = email_request.json()
        email = email_request_json.get('email')

        # return JsonResponse({'access': access_token, 'email': email})

        '''회원가입 or 로그인 요청'''
        try:
            user = User.objects.get(email=email)
            
            # 기존에 가입된 유저의 Provider가 google이 아니면 에러 발생 아닐시 정상 로그인
            # 다른 sns로 가입된 유저
            social_user = SocialAccount.objects.get(user=user)
            if social_user is None:
                return JsonResponse({'error': '회원가입 정보가 없습니다.'}, status=status.HTTP_400_BAD_REQUEST)
            if social_user.provider != 'google':
                return JsonResponse({'error': '일치하는 정보가 없습니다.'}, status=status.HTTP_400_BAD_REQUEST)
            
            # 기존에 Google로 가입된 유저
            data = {'access_token': access_token, 'code':  code}
            accept = requests.post(f"{BASE_URL}api/accounts/google/login/finish/", data=data)
            accept_status = accept.status_code
            
            if accept_status != 200:
                return JsonResponse({'error': '로그인에 실패했습니다.'}, status=accept_status)
            accept_json = accept.json()
            accept_json.pop('user', None)
            return JsonResponse(accept_json)
        
        except User.DoesNotExist:
            # 전달받은 이메일로 가입된 유저가 없으면 회원가입
            data = {'access_token': access_token, 'code':  code}
            accept = requests.post(f"{BASE_URL}api/accounts/google/login/finish/", data=data)
            accept_status = accept.status_code
            
            if accept_status != 200:
                return JsonResponse({'error': '로그인에 실패했습니다.'}, status=accept_status)
            accept_json = accept.json()
            accept_json.pop('user', None)
            return JsonResponse(accept_json)
        

# 구글 소셜 로그인뷰
class GoogleSocialView(SocialLoginView):
    adapter_class = google_view.GoogleOAuth2Adapter
    callback_url = GOOGLE_CALLBACK_URI
    client_class = OAuth2Client

# 카카오 소셜 로그인
class KakaoLoginView(APIView):
    '''코드 요청'''
    def get(self, request):
        client_id = getattr(settings, 'KAKAO_CLIENT_ID')
        return redirect(f"https://kauth.kakao.com/oauth/authorize?client_id={client_id}&redirect_uri={KAKAO_CALLBACK_URI}&response_type=code")
    
class KakaoCallbackView(APIView):
    '''콜백'''
    def get(self, request):
        client_id = getattr(settings, 'KAKAO_CLIENT_ID')
        redirect_uri = KAKAO_CALLBACK_URI
        code = request.GET.get('code')
        
        # 토큰 요청
        token_request = requests.post(
            f"https://kauth.kakao.com/oauth/token?grant_type=authorization_code&client_id={client_id}&redirect_uri={redirect_uri}&code={code}"
        )
        # json 형태로 변환 & 에러 처리
        token_request_json = token_request.json()
        error = token_request_json.get("error")
        if error is not None:
            return JsonResponse({'error': error}, status=status.HTTP_400_BAD_REQUEST)
        access_token = token_request_json.get("access_token")

        # 사용자 정보 요청
        profile_request = requests.get(
            "https://kapi.kakao.com/v2/user/me", headers={"Authorization": f"Bearer {access_token}"}
        )
        profile_request_json = profile_request.json()
        kakao_account = profile_request_json.get("kakao_account")
        
        # print(kakao_account)
        email = kakao_account.get("email")


        '''회원가입 or 로그인 요청'''
        try:
            user = User.objects.get(email=email)
            
            # 기존에 가입된 유저의 Provider가 kakao가 아니면 에러 발생 아닐시 정상 로그인
            # 다른 sns로 가입된 유저
            social_user = SocialAccount.objects.get(user=user)
            if social_user is None:
                return JsonResponse({'error': '회원가입 정보가 없습니다.'}, status=status.HTTP_400_BAD_REQUEST)
            if social_user.provider != 'kakao':
                return JsonResponse({'error': '일치하는 정보가 없습니다.'}, status=status.HTTP_400_BAD_REQUEST)
            
            # 기존에 다른이메일로 가입된 유저
            data = {'access_token': access_token, 'code':  code}
            accept = requests.post(f"{BASE_URL}api/accounts/kakao/login/finish/", data=data)
            accept_status = accept.status_code
            
            if accept_status != 200:
                return JsonResponse({'error': '회원가입에 실패했습니다.'}, status=accept_status)
            accept_json = accept.json()
            accept_json.pop('user', None)
            return JsonResponse(accept_json)
        
        except User.DoesNotExist:
            # 기존에 가입된 유저가 없으면 새로 가입
            data = {'access_token': access_token, 'code':  code}
            accept = requests.post(f"{BASE_URL}api/accounts/kakao/login/finish/", data=data)
            accept_status = accept.status_code
            if accept_status != 200:
                return JsonResponse({'error': '회원가입에 실패했습니다.'}, status=accept_status)
            accept_json = accept.json()
            accept_json.pop('user', None)
            return JsonResponse(accept_json)
        
class KakaoSocialView(SocialLoginView):
    adapter_class = kakao_view.KakaoOAuth2Adapter
    callback_url = KAKAO_CALLBACK_URI
    client_class = OAuth2Client