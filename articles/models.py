from django.db import models
from django.conf import settings
try:
    import markdown
except ImportError:
    markdown = None
from django.utils.translation import gettext_lazy as _

class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        self.name = self.name.strip().lower()  # 태그 정규화

    def __str__(self):
        return self.name

# model 에 수정 사항이 생길 때마다 makemigrations, migrate 진행하기

class Article(models.Model):
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='articles',
        verbose_name=_('작성자')
    )
    title = models.CharField(_('제목'), max_length=200)
    content = models.TextField(_('내용'))
    image = models.ImageField(upload_to='article_images/', null=True, blank=True)
    created_at = models.DateTimeField(_('작성일'), auto_now_add=True)
    updated_at = models.DateTimeField(_('수정일'), auto_now=True)
    likes = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through='ArticleLike',
        related_name='liked_articles',
        verbose_name=_('좋아요')
    )
    views = models.PositiveIntegerField(_('조회수'), default=0)  # 조회수
    hashtags = models.CharField(max_length=500, blank=True)  # 해시태그
    reports = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through='ArticleReport',
        related_name='reported_articles'
    )
    content_raw = models.TextField(_('원본 내용'), blank=True)
    content_html = models.TextField(_('HTML 내용'), blank=True)
    tags = models.ManyToManyField(Tag, related_name='articles', blank=True)

    def __str__(self):
        return self.title

    def increase_views(self):
        self.views += 1
        self.save()

    @property
    def image_count(self):
        if self.pk:
            return self.images.count()
        return 0

    def clean(self):
        from django.core.exceptions import ValidationError
        super().clean()

    def save(self, *args, **kwargs):
        if not self.content_html and self.content:
            self.content_html = self.content
        if not self.content_raw and self.content:
            self.content_raw = self.content
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['-created_at']
        verbose_name = _('게시글')
        verbose_name_plural = _('게시글들')
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['-views']),
        ]


class ArticleLike(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    article = models.ForeignKey('Article', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'article')


class ArticleReport(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    reason = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['article', 'user']


class Comment(models.Model):
    article = models.ForeignKey(
        Article, 
        on_delete=models.CASCADE, 
        related_name='comments',
        verbose_name=_('게시글')
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
        verbose_name=_('작성자')
    )
    content = models.TextField(_('내용'))
    created_at = models.DateTimeField(_('작성일'), auto_now_add=True)
    updated_at = models.DateTimeField(_('수정일'), auto_now=True)
    like_users = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='like_comments') # 댓글 좋아요
    
    class Meta:
        ordering = ['created_at']
        verbose_name = _('댓글')
        verbose_name_plural = _('댓글들')

    def __str__(self):
        return f'{self.author.nickname}의 댓글'


class ArticleImage(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='images') # FK
    image = models.ImageField('이미지', upload_to='images/') # media/images/ 경로에 이미지 저장
    uploaded_at = models.DateTimeField('업로드일', auto_now_add=True)
    
    def __str__(self):
        return f"Image for {self.article.title}"