from rest_framework import serializers
from .models import Article, Comment

# serializer - 장고에서 쓰는 파이썬 객체, 쿼리셋같이 복잡한 데이터를 JSON, XML 등의 간단한 데이터로 변환하는 작업

class ArticleListSerializer(serializers.ModelSerializer):
    '''게시글 목록 조회 serializer'''
    class Meta:
        model = Article
        fields = ('id','user','title','created_at','view_count')
        read_only_fields = ('user',) # user 필드는 읽기 전용 - 수정 할 수 없는 필드


class ArticleDetailSerializer(serializers.ModelSerializer):
    '''게시글 상세 조회 및 생성, 수정, 삭제 serializer'''
    user = serializers.ReadOnlyField(source='user.email') # user 필드를 읽기 전용 필드로 정의, 그 값으로 유저의 이메일을 출력
    
    class Meta:
        model = Article
        fields = ('id', 'user', 'title', 'content', 'created_at', 'updated_at', 'view_count','article_image')
        
    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated: # 현재 요청한 사용자가 게시글에 좋아요를 했는지
            return obj.like_users.filter(pk=request.user.pk).exists()
        return False

class CommentSerializer(serializers.ModelSerializer):
    '''댓글 조회 및 생성 serializer'''
    user = serializers.ReadOnlyField(source='user.email')
    like_count = serializers.IntegerField(source='like_users.count', read_only=True)
    is_liked = serializers.SerializerMethodField() # 좋아요 여부 - 가상 필드
    
    class Meta:
        model = Comment
        fields = ('id','article','user', 'content','created_at','updated_at','like_users','like_count','is_liked')
        read_only_fields = ('article', 'like_users') # 댓글 생성시 필요 없는 fields 명시
        
    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.like_users.filter(pk=request.user.pk).exists() # 현재 좋아요를 한 사람이 목록에 있는지 exists() 로 확인 -> 맞다면 True
        return False