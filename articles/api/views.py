from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from django.shortcuts import get_object_or_404
from django.db.models import Count, Q
from ..models import Article, Comment, ArticleLike
from ..serializers import ArticleSerializer, CommentSerializer, ArticleListSerializer, ArticleDetailSerializer

class ArticleListCreateAPIView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request):
        filter_type = request.query_params.get('filter', 'all')
        sort_type = request.query_params.get('sort', 'latest')
        
        articles = Article.objects.select_related('author').prefetch_related(
            'likes', 'comments'
        ).all()
        
        # 필터링
        if filter_type != 'all' and request.user.is_authenticated:
            if filter_type == 'my':
                articles = articles.filter(author=request.user)
            elif filter_type == 'liked':
                articles = articles.filter(likes=request.user)
                
        # 정렬
        if sort_type == 'latest':
            articles = articles.order_by('-created_at')
        elif sort_type == 'views':
            articles = articles.order_by('-views')
        elif sort_type == 'likes':
            articles = articles.annotate(
                likes_count=Count('likes')
            ).order_by('-likes_count', '-created_at')
            
        serializer = ArticleListSerializer(
            articles, 
            many=True, 
            context={'request': request}
        )
        
        return Response({
            'results': serializer.data,
            'count': articles.count(),
            'filter': filter_type,
            'sort': sort_type
        })

    def post(self, request):
        serializer = ArticleSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(author=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CommentListCreateAPIView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request, pk):
        article = get_object_or_404(Article, pk=pk)
        comments = Comment.objects.filter(article=article)
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)

    def post(self, request, pk):
        article = get_object_or_404(Article, pk=pk)
        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(article=article, author=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ArticleDetailAPIView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_article(self, pk):
        return get_object_or_404(Article, pk=pk)

    def get(self, request, pk):
        article = self.get_article(pk)
        serializer = ArticleSerializer(article, context={'request': request})
        return Response(serializer.data)

    def put(self, request, pk):
        article = self.get_article(pk)
        if request.user != article.author:
            return Response(status=status.HTTP_403_FORBIDDEN)
        serializer = ArticleSerializer(article, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        article = self.get_article(pk)
        if request.user != article.author:
            return Response(status=status.HTTP_403_FORBIDDEN)
        article.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class ArticleLikeAPIView(APIView):
    def post(self, request, pk):
        article = get_object_or_404(Article, pk=pk)
        if request.user in article.likes.all():
            article.likes.remove(request.user)
            liked = False
        else:
            article.likes.add(request.user)
            liked = True
        return Response({
            'liked': liked,
            'likes_count': article.likes.count()
        })

class ArticleDeleteAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk):
        article = get_object_or_404(Article, pk=pk)
        if request.user != article.author:
            return Response(
                {'error': '삭제 권한이 없습니다.'},
                status=status.HTTP_403_FORBIDDEN
            )
        article.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
