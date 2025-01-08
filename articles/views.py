from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.views import APIView
from .models import Article, Comment, ArticleImage
from .serializers import ArticleListSerializer, ArticleDetailSerializer, CommentSerializer
from django.core.cache import cache


class ArticleListCreate(APIView):
    '''게시글 조회 및 생성 클래스'''
    # 권한 명시 : settings.py REST_FRAMEWORK 에 권한 전역 설정이 있으므로 명시해줘야 함 -> 권한 명시 없으면 전역 설정이 적용됨
    permission_classes = [IsAuthenticatedOrReadOnly] # 작성은 인증된 사용자만, 조회는 누구나 가능

    def get(self, request):
        '''게시글 목록 조회'''
        # 데이터 가져오기
        article = Article.objects.all()

        # 직렬화 : 가본적으로 Serializer는 단일 객체를 직렬화하도록 설계되어 있어서 many=True 옵션을 줌
        serializer = ArticleListSerializer(article, many=True)

        # 데이터 돌려주기
        return Response(serializer.data)

    def post(self, request):
        '''게시글 생성'''
        serializer = ArticleDetailSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True): # 유효성 검사: 유효하지 않으면 400 에러 반환
            article = serializer.save(user=request.user)  # 게시글 저장
            
            images = request.data.getlist('images') # 게시글 이미지
            if len(images) > 5:
                return Response({'message': '이미지는 최대 5개까지 업로드 가능합니다.'}, status=status.HTTP_400_BAD_REQUEST)
            
            for image in images:
                ArticleImage.objects.create(article=article, image=image)  # 이미지 저장

            return Response(serializer.data, status=status.HTTP_201_CREATED)

class ArticleDetail(APIView):
    def get_object(self, articleId):
        # pk 값이 없을 시 404 error 출력
        return get_object_or_404(Article, pk=articleId)

    def get(self, request, articleId):
        '''게시글 상세 조회'''
        # 1. article pk 조회
        article = self.get_object(articleId)
        
        '''조회수 기능'''
        # 로그인한 사용자이고 작성자가 아닌 경우에만 조회수 증가
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
        serializer = ArticleDetailSerializer(article)
        return Response(serializer.data)

    def put(self, request, articleId):
        '''게시글 수정'''
        article = self.get_object(articleId)
        serializer = ArticleDetailSerializer(
            article,
            data=request.data, # 요청에 넣은 데이터
            partial=True, # 부분적 수정 허용
        )
        if serializer.is_valid(raise_exception=True):
            article = serializer.save()
            # 이미지 처리
            images = request.FILES.getlist('images')  # 새로 업로드된 이미지
            if len(images) > 5:
                return Response(
                    {'message': '이미지는 최대 5개까지 업로드 가능합니다.'},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # 기존 이미지 전체 삭제
            delete_images = request.data.get('delete_images', False)
            if delete_images:  # 삭제 옵션이 있는 경우
                article.images.all().delete()

            # 새 이미지 추가
            for image in images:
                ArticleImage.objects.create(article=article, image=image)

            return Response(ArticleDetailSerializer(article).data)

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
        if serializer.is_valid(raise_exception=True): # 유효성 검사: 유효하지 않으면 400 에러 반환
            serializer.save(user=request.user, article=article)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
#        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)  # raise_exception=True 를 사용해서 필요 없음

    def put(self, request, articleId):
        '''댓글 수정'''
        article = self.get_article(articleId)
        comment = get_object_or_404(Comment, pk=request.data['commentId'], article=article) # request.data['commentId'] -> 요청시 commentId 필요
        serializer = CommentSerializer(
            comment,
            data=request.data,
            partial=True,
        )
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data)

    def delete(self, request, articleId):
        '''댓글 삭제'''
        article = self.get_article(articleId)
        comment = get_object_or_404(Comment, pk=request.data['commentId'], article=article) # request.data['commentId'] -> 요청시 commentId 필요
        comment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


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


class ArticleDetailLike(APIView):
    '''게시글 좋아요 기능'''
    def get_article(self, articleId):
        return get_object_or_404(Article, pk=articleId)
    
    def post(self, request, articleId):
        article = self.get_article(articleId)
        user = request.user
        
        # 이미 좋아요를 눌렀는지 확인
        if article.like_users.filter(pk=user.pk).exists():
            # 좋아요 취소
            article.like_users.remove(user)
            message = "게시글 좋아요가 취소되었습니다"
        else:
            # 좋아요
            article.like_users.add(user)
            message = "게시글을 좋아요 했습니다"

        # 댓글 정보를 serializer 를 통해 반환
        serializer = ArticleDetailSerializer(article, context={'request':request})
        
        return Response({
            'message': message,
            'comment': serializer.data
            }, status=status.HTTP_200_OK)