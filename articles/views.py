from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.views import APIView
from .models import Article, Comment
from .serializers import ArticleListSerializer, ArticleDetailSerializer
from django.core.cache import cache


class ArticleListCreate(APIView):
    '''게시글 조회 및 생성 클래스'''
    # 권한 명시 : settings.py REST_FRAMEWORK
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request):
        '''게시글 목록 조회'''
        # 1. 데이터 가져오기
        products = Article.objects.all()

        # 2. 직렬화
        serializer = ArticleListSerializer(products, many=True)

        # 3. 데이터 돌려주기
        return Response(serializer.data)

    def post(self, request):
        '''게시글 생성'''
        serializer = ArticleDetailSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True): # 유효성 검사
            serializer.save(user=request.user) # permission 을 readonly 로 했기에 인자 넣어주기
            return Response(serializer.data, status=status.HTTP_201_CREATED)