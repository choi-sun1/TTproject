from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from .serializers import SignupSerializer, UserProfileSerializer, UserUpdateSerializer


# Create your views here.
def signup(request):
    serializer = SignupSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({
            'message': '회원가입이 성공적으로 완료되었습니다.'
        }, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def login(request):
        username = request.POST.get('username')
        password = request.POST.get('password')

        # 사용자 인증
        user = authenticate(request, username=username, password=password)
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


def logout(request):
    print('---')
    try:
        refresh_token = request.data.get("refresh")
        print(refresh_token)
        token = RefreshToken(refresh_token)
        print(token)
        token.blacklist()
        print('---')
        return Response({"message": "로그아웃 성공"})
    except Exception:
        return Response({"error": "로그아웃 실패"}, 
            status=status.HTTP_400_BAD_REQUEST)



def profile(request):
    user = request.user # JWT 인증을 통해 얻은 현재 사용자

    if request.method == 'GET':
        serializer = UserProfileSerializer(user, context={'request':request})
        return Response(serializer.data, status=200)
    
    if request.method in ('PUT','PATCH'):
        serializer = UserUpdateSerializer(instance=user, data=request.data, partial=True)  # partial=True로 일부 업데이트 허용

        if serializer not in serializer.fields:
            return Response({
                'message':'이 정보는 수정할 수 없습니다.'
            }, status=status.HTTP_400_BAD_REQUEST)

        if serializer.is_valid():
            serializer.save()  
            return Response({
                'message':'회원정보가 성공적으로 수정되었습니다.',
                'user': serializer.data
            }, status=status.HTTP_200_OK)


        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
