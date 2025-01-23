from django.contrib import admin
from .models import Article, Comment, ArticleLike, ArticleReport, ArticleImage, Tag

@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'created_at', 'views', 'total_likes')
    list_filter = ('created_at',)
    search_fields = ('title', 'content', 'author__email')
    readonly_fields = ('views',)
    
    def total_likes(self, obj):
        return obj.likes.count()
    total_likes.short_description = '좋아요 수'

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('content', 'article', 'author', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('content', 'author__email')

admin.site.register(ArticleLike)
admin.site.register(ArticleReport)
admin.site.register(ArticleImage)
admin.site.register(Tag)
