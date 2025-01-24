from django.urls import path
from . import views

app_name = 'articles'

urlpatterns = [
    # Frontend URLs
    path('list/', views.article_list, name='list'),  # URL 패턴 수정
    path('create/', views.article_create, name='create'),  # create view URL 확인
    path('web/detail/<int:pk>/', views.article_detail, name='detail'),
    path('web/edit/<int:pk>/', views.article_edit, name='edit'),

    # API URLs
    path('', views.ArticleListCreateAPIView.as_view(), name='article-list'),
    path('create/', views.ArticleListCreateAPIView.as_view(), name='article-create'),
    path('<int:pk>/', views.ArticleDetailAPIView.as_view(), name='article-detail'),
    path('<int:pk>/update/', views.ArticleUpdateAPIView.as_view(), name='article-update'),
    path('<int:pk>/delete/', views.ArticleDeleteAPIView.as_view(), name='article-delete'),
    path('<int:pk>/like/', views.ArticleLikeAPIView.as_view(), name='article-like'),
    path('<int:article_id>/comments/', views.CommentListCreateAPIView.as_view(), name='comment-create'),
    path('<int:article_id>/comments/<int:comment_id>/', views.CommentDetailAPIView.as_view(), name='comment-delete'),
]