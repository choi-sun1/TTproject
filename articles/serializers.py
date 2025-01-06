from rest_framework import serializers
from .models import Article, Comment

# serializer - 장고에서 쓰는 파이썬 객체, 쿼리셋같이 복잡한 데이터를 JSON, XML 등의 간단한 데이터로 변환하는 작업

class ArticleListSerializer(serializers.ModelSerializer):
    '''게시글 목록 조회 serializer'''
    class Meta:
        model = Article
        fields = ('id','user','title','created_at','view_count')
        read_only_fields = ('user',) # user 필드는 읽기 전용 - 수정 할 수 없는 필드


# 게시글 상세 조회 및 생성 Serializer
class ArticleDetailSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.email') # user 필드를 읽기 전용 필드로 정의, 그 값으로 유저의 이메일을 출력
    
    class Meta:
        model = Article
        fields = ('id', 'user', 'title', 'content', 'created_at', 'updated_at', 'view_count')

