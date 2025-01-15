from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.shortcuts import get_object_or_404, redirect, render
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.views import APIView
from .models import User, RelatedModel
from .serializers import SignupSerializer, UserProfileSerializer, UserUpdateSerializer
from django.core.cache import cache
from django.contrib.auth import authenticate, login, logout
from rest_framework_simplejwt.tokens import RefreshToken
from django.http import JsonResponse
from articles.models import Article
from django.contrib import messages
from .forms import UserRegisterForm, UserLoginForm
from django.contrib.auth.decorators import login_required
from board.models import Post
from stays.models import Booking
from datetime import date


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
    authentication_classes = [] 
    permission_classes = [] 
    
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
        
            serializer.save()
            return Response({
                'message': '회원정보가 성공적으로 수정되었습니다.',
                'user': serializer.data
            }, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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


def register_view(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = UserRegisterForm()
    return render(request, 'accounts/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, '로그인되었습니다.')
                return redirect('home')
            else:
                messages.error(request, '아이디 또는 비밀번호가 올바르지 않습니다.')
    else:
        form = UserLoginForm()
    return render(request, 'accounts/login.html', {'form': form})

@login_required
def logout_view(request):
    logout(request)
    messages.success(request, '로그아웃되었습니다.')
    return redirect('home')

@login_required
def profile_view(request, username):
    user = get_object_or_404(User, username=username)
    context = {
        'profile_user': user,
        'posts': Post.objects.filter(author=user).order_by('-created_at')[:5],
        'bookings': Booking.objects.filter(user=user).order_by('-created_at')[:5],
        'today': date.today().strftime('%Y-%m-%d')
    }
    return render(request, 'accounts/profile.html', context)

@login_required
def profile_edit(request):
    if request.method == 'POST':
        user = request.user
        user.nickname = request.POST.get('nickname', user.nickname)
        user.gender = request.POST.get('gender', user.gender)
        birth_date = request.POST.get('birth_date')
        if birth_date:
            user.birth_date = birth_date
        user.bio = request.POST.get('bio', user.bio)
        
        if 'profile_image' in request.FILES:
            user.profile_image = request.FILES['profile_image']
        
        user.save()
        messages.success(request, '프로필이 성공적으로 수정되었습니다.')
        return redirect('accounts:profile', username=user.username)
    
    return render(request, 'accounts/profile_edit.html')
