from rest_framework import serializers
from .models import Article, Comment, ArticleImage, Tag, ArticleReport
from django.contrib.auth import get_user_model

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'nickname', 'profile_image']

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name']

class ArticleImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ArticleImage
        fields = ['id', 'image', 'uploaded_at']

class CommentSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    likes_count = serializers.IntegerField(source='like_users.count', read_only=True)
    
    class Meta:
        model = Comment
        fields = ['id', 'author', 'content', 'created_at', 'likes_count']
        read_only_fields = ['author']

class ArticleReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = ArticleReport
        fields = ['id', 'article', 'user', 'reason', 'created_at']
        read_only_fields = ['user']

class ArticleListSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    comments_count = serializers.IntegerField(source='comments.count', read_only=True)
    likes_count = serializers.IntegerField(source='likes.count', read_only=True)

    class Meta:
        model = Article
        fields = [
            'id', 'author', 'title', 'created_at',
            'views', 'likes_count', 'comments_count'
        ]

    def to_representation(self, instance):
        # 성능 최적화를 위한 쿼리 최적화
        if isinstance(instance, Article):
            instance = Article.objects.select_related('author').prefetch_related(
                'comments', 'likes'
            ).get(id=instance.id)
        return super().to_representation(instance)

class ArticleDetailSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    comments = CommentSerializer(many=True, read_only=True)
    images = ArticleImageSerializer(many=True, read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    likes_count = serializers.IntegerField(source='likes.count', read_only=True)
    is_liked = serializers.SerializerMethodField()

    class Meta:
        model = Article
        fields = [
            'id', 'author', 'title', 'content', 'content_raw', 'content_html',
            'created_at', 'updated_at', 'views', 'likes_count', 'is_liked',
            'comments', 'images', 'tags', 'hashtags'
        ]
        read_only_fields = ['views', 'likes_count']

    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.likes.filter(id=request.user.id).exists()
        return False

    def to_representation(self, instance):
        # 성능 최적화를 위한 쿼리 최적화
        if isinstance(instance, Article):
            instance = Article.objects.select_related('author').prefetch_related(
                'comments', 'comments__author',
                'images', 'tags', 'likes'
            ).get(id=instance.id)
        return super().to_representation(instance)

class ArticleSerializer(ArticleDetailSerializer):
    """
    게시글 생성 및 수정을 위한 Serializer
    ArticleDetailSerializer를 상속받아 사용
    """
    pass

class ArticleLikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = ['id', 'likes']
        read_only_fields = ['likes']