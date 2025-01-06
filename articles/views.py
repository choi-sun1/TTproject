from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.views import APIView
from .models import Article, Comment
from .serializers import ArticleListSerializer, ArticleDetailSerializer, CommentSerializer
from django.core.cache import cache


class ArticleListCreate(APIView):
    '''게시글 조회 및 생성 클래스'''
    # 권한 명시 : settings.py REST_FRAMEWORK
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request):
        '''게시글 목록 조회'''
        # 1. 데이터 가져오기
        article = Article.objects.all()

        # 2. 직렬화
        serializer = ArticleListSerializer(article, many=True)

        # 3. 데이터 돌려주기
        return Response(serializer.data)

    def post(self, request):
        '''게시글 생성'''
        serializer = ArticleDetailSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True): # 유효성 검사
            serializer.save(user=request.user) # permission 을 readonly 로 했기에 인자 넣어주기
            return Response(serializer.data, status=status.HTTP_201_CREATED)

class ArticleDetail(APIView):
    def get_object(self, articleId):
        # pk 값이 없을 시 404 error 출력
        return get_object_or_404(Article, pk=articleId)

    def get(self, request, articleId):
        '''게시글 상세 조회'''
        # 1. article pk 조회
        article = self.get_object(articleId)
        
        # 수정한 조회수
        # 로그인한 사용자이고 작성자가 아닌 경우에만 조회수 증가 처리
        # 24시간 동안 같은 IP에서 같은 게시글 조회 시 조회수가 증가하지 않음
        if request.user != article.user:
            # 해당 사용자의 IP와 게시글 ID로 캐시 키를 생성
            cache_key = f"view_count_{request.META.get('REMOTE_ADDR')}_{articleId}"
        
            # 캐시에 없는 경우에만 조회수 증가
            if not cache.get(cache_key):
                article.view_count += 1
                article.save()
                # 캐시 저장 (24시간 유효)
                cache.set(cache_key, True, 60*60*24)
        
        # 기존의 조회수
        # article.view_count += 1
        # article.save()
        
        # 2. 직렬화
        serializer = ArticleDetailSerializer(article)
        # 3. 반환
        return Response(serializer.data)

    def put(self, request, articleId):
        '''게시글 수정'''
        article = self.get_object(articleId)
        serializer = ArticleDetailSerializer(
            article,
            data=request.data,
            partial=True, # 부분적 수정 허용
        )
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data)

    def delete(self, request, articleId):
        '''게시글 삭제'''
        article = self.get_object(articleId)
        article.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CommentListCreate(APIView):
    '''댓글 CRUD'''
    def get_article(self, articleId):
        return get_object_or_404(Article, pk=articleId)


    def get(self, request, articleId):
        '''댓글 조회'''
        article = self.get_article(articleId)
        comments = article.comments.all() # 역참조로 모든 댓글 가져오기
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)

    def post(self, request, articleId):
        '''댓글 생성'''
        article = self.get_article(articleId)
        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user, article=article)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CommentLike(APIView):
    '''댓글 좋아요 기능'''
    def get_article(self, articleId):
        return get_object_or_404(Article, pk=articleId)
    
    def get_comment(self, article, commentId):
        return get_object_or_404(Comment, pk=commentId, article=article)

    def post(self, request, articleId, commentId):
        article = self.get_article(articleId)
        comment = self.get_comment(article, commentId)
        user = request.user
        
        # 이미 좋아요를 눌렀는지 확인
        if comment.like_users.filter(pk=user.pk).exists():
            # 좋아요 취소
            comment.like_users.remove(user)
            message = "댓글 좋아요가 취소되었습니다."
        else:
            # 좋아요 추가
            comment.like_users.add(user)
            message = "댓글을 좋아요 했습니다."

        # 댓글 정보를 serializer를 통해 반환
        serializer = CommentSerializer(comment, context={'request': request})
        
        return Response({
            'message': message,
            'comment': serializer.data
        }, status=status.HTTP_200_OK)
