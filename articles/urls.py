from django.urls import path, include
from . import views

# 'api/articles/'
urlpatterns = [
    path('', views.ArticleListCreate.as_view(), name='article_list_create'), # 게시글 목록 조회, 생성
    path('<int:articleId>/', views.ArticleDetail.as_view(), name='article_detail'), # 게시글 상세 조회, 수정, 삭제
    path('<int:articleId>/comments/', views.CommentListCreate.as_view(), name='comments'), # 댓글 조회, 생성

]