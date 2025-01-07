from django.db import models
from django.conf import settings

# model 에 수정 사항이 생길 때마다 makemigrations, migrate 진행하기

class Article(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='articles') # FK
    title = models.CharField('제목',max_length=200)
    content = models.TextField('내용')
    created_at = models.DateTimeField('작성일', auto_now_add=True)
    updated_at = models.DateTimeField('수정일', auto_now=True)
    view_count = models.PositiveIntegerField('조회수', default=0) # 조회수 필드
    like_users = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='like_articles') # 게시글 좋아요
    article_image = models.ImageField('게시글 이미지', upload_to='article_images/', blank=True, null=True) # media/article_images/ 경로에 이미지 저장
    
    def __str__(self):
        return self.title


class Comment(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='comments') # FK
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE) # FK
    content = models.TextField('내용')
    created_at = models.DateTimeField('작성일', auto_now_add=True)
    updated_at = models.DateTimeField('수정일', auto_now=True)
    like_users = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='like_comments') # 댓글 좋아요
    
    def __str__(self):
        return f'{self.user} - {self.content}'