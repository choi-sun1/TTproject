from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Article

def article_list(request):
    articles = Article.objects.all().order_by('-created_at')
    return render(request, 'articles/list.html', {'articles': articles})

@login_required
def article_create(request):
    if request.method == 'POST':
        # Create article logic
        return redirect('articles:list')
    return render(request, 'articles/create.html')

def article_detail(request, pk):
    article = get_object_or_404(Article, pk=pk)
    return render(request, 'articles/detail.html', {'article': article})

@login_required
def article_edit(request, pk):
    article = get_object_or_404(Article, pk=pk)
    if request.user != article.author:
        return redirect('articles:detail', pk=pk)
    if request.method == 'POST':
        # Edit article logic
        return redirect('articles:detail', pk=pk)
    return render(request, 'articles/edit.html', {'article': article})

from rest_framework.response import Response
from rest_framework import status, viewsets, filters
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework.views import APIView
from rest_framework.decorators import action
from django.db.models import Count, Q
from django_filters.rest_framework import DjangoFilterBackend
from .models import Article, Comment, ArticleImage, ArticleReport, ArticleLike
from .serializers import ArticleListSerializer, ArticleDetailSerializer, CommentSerializer, ArticleSerializer, ArticleReportSerializer
from django.core.cache import cache
from django.views.generic import CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from .forms import ArticleForm


class ArticleListCreateAPIView(APIView):
    """
    게시글 목록 조회 및 생성 API
    
    get:
        게시글 목록을 반환합니다.
        
        Parameters:
            - page: 페이지 번호
            - search: 검색어
            - ordering: 정렬 기준 (created_at, views, likes)
            
    post:
        새로운 게시글을 생성합니다.
        
        Parameters:
            - title: 게시글 제목
            - content: 게시글 내용
            - image: 이미지 파일 (선택)
    """
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request):
        articles = Article.objects.all()
        serializer = ArticleSerializer(articles, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = ArticleSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(author=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ArticleDetailAPIView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request, pk):
        article = get_object_or_404(Article, pk=pk)
        serializer = ArticleSerializer(article)
        return Response(serializer.data)

    def put(self, request, pk):
        article = get_object_or_404(Article, pk=pk)
        if request.user != article.author:
            return Response(status=status.HTTP_403_FORBIDDEN)
        
        serializer = ArticleSerializer(article, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        article = get_object_or_404(Article, pk=pk)
        if request.user != article.author:
            return Response(status=status.HTTP_403_FORBIDDEN)
        article.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

@login_required
def article_like(request, pk):
    article = get_object_or_404(Article, pk=pk)
    if request.user in article.likes.all():
        article.likes.remove(request.user)
    else:
        article.likes.add(request.user)
    return redirect('articles:detail', pk=pk)


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


class ArticleViewSet(viewsets.ModelViewSet):
    serializer_class = ArticleSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter
    ]
    filterset_fields = ['author', 'tags__name']
    search_fields = ['title', 'content', 'tags__name']
    ordering_fields = ['created_at', 'views', 'likes_count']

    def get_queryset(self):
        queryset = super().get_queryset()
        sort_by = self.request.query_params.get('sort')

        if sort_by == 'popular':
            # 인기순 (좋아요 + 조회수)
            return queryset.annotate(
                popularity=Count('likes') + models.F('views')
            ).order_by('-popularity')
            
        return queryset

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.increase_views()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def report(self, request, pk=None):
        article = self.get_object()
        reason = request.data.get('reason')
        
        if not reason:
            return Response(
                {'error': '신고 사유를 입력해주세요.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        report, created = ArticleReport.objects.get_or_create(
            article=article,
            user=request.user,
            defaults={'reason': reason}
        )

        if not created:
            return Response(
                {'error': '이미 신고한 게시글입니다.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response({'message': '신고가 접수되었습니다.'})

    def create(self, request, *args, **kwargs):
        """게시글 작성 메서드"""
        # 이미지 개수 제한 확인
        images = request.FILES.getlist('images', [])
        if len(images) > 5:
            return Response(
                {'error': '이미지는 최대 5개까지만 업로드할 수 있습니다.'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        article = serializer.save(author=request.user)
        
        # 해시태그 처리
        hashtags = request.data.get('hashtags', '')
        if hashtags:
            article.hashtags = hashtags
            article.save()
            
        # 이미지 처리
        for image in images:
            ArticleImage.objects.create(article=article, image=image)
            
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        """게시글 수정 메서드"""
        instance = self.get_object()
        
        # 이미지 개수 제한 확인
        current_images = instance.images.count()
        new_images = len(request.FILES.getlist('images', []))
        if current_images + new_images > 5:
            return Response(
                {'error': '이미지는 최대 5개까지만 업로드할 수 있습니다.'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        # 이미지 처리
        if 'delete_images' in request.data:
            instance.images.all().delete()
            
        for image in request.FILES.getlist('images', []):
            ArticleImage.objects.create(article=instance, image=image)
            
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        return Response(serializer.data)


from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView
from django.urls import reverse_lazy
from .forms import ArticleForm
from .models import Article, ArticleImage

class ArticleCreateView(LoginRequiredMixin, CreateView):
    model = Article
    form_class = ArticleForm
    template_name = 'articles/create.html'
    success_url = reverse_lazy('articles:list')

    def form_valid(self, form):
        # 이미지 개수 검증
        images = self.request.FILES.getlist('images')
        if len(images) > 5:
            form.add_error(None, "이미지는 최대 5개까지만 업로드할 수 있습니다.")
            return self.form_invalid(form)

        form.instance.author = self.request.user
        response = super().form_valid(form)
        article = self.object

        # 이미지 저장
        for image in images:
            ArticleImage.objects.create(article=article, image=image)

        # 태그 처리
        tags = form.cleaned_data.get('tags')
        if tags:
            tag_list = [tag.strip() for tag in tags.split(',')]
            article.tags.add(*tag_list)

        messages.success(self.request, '게시글이 성공적으로 등록되었습니다.')
        return response

    def form_invalid(self, form):
        messages.error(self.request, '입력하신 정보를 다시 확인해주세요.')
        return super().form_invalid(form)

from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import Article
from .serializers import ArticleSerializer, ArticleListSerializer, ArticleDetailSerializer
from django.shortcuts import render

# API Views
class ArticleListCreateAPIView(generics.ListCreateAPIView):
    queryset = Article.objects.all()
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ArticleSerializer
        return ArticleListSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

class ArticleDetailAPIView(generics.RetrieveAPIView):
    queryset = Article.objects.all()
    serializer_class = ArticleDetailSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

class ArticleUpdateAPIView(generics.UpdateAPIView):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Article.objects.filter(author=self.request.user)

class ArticleDeleteAPIView(generics.DestroyAPIView):
    queryset = Article.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Article.objects.filter(author=self.request.user)

class ArticleLikeAPIView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        article = get_object_or_404(Article, pk=pk)
        if request.user in article.likes.all():
            article.likes.remove(request.user)
            return Response({'liked': False})
        article.likes.add(request.user)
        return Response({'liked': True})

class CommentListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        return Comment.objects.filter(article_id=self.kwargs['article_id'])

    def perform_create(self, serializer):
        article = get_object_or_404(Article, pk=self.kwargs['article_id'])
        serializer.save(
            author=self.request.user,
            article=article
        )

class CommentDetailAPIView(generics.RetrieveDestroyAPIView):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_url_kwarg = 'comment_id'

    def get_queryset(self):
        return Comment.objects.filter(
            article_id=self.kwargs['article_id'],
            author=self.request.user
        )

# Template Views
def article_list(request):
    return render(request, 'articles/article_list.html')

def article_create(request):
    return render(request, 'articles/article_form.html')

def article_detail(request, pk):
    return render(request, 'articles/article_detail.html')

def article_edit(request, pk):
    return render(request, 'articles/article_form.html')