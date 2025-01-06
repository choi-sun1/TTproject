from django.urls import path, include
from . import views

# 'api/articles/'
urlpatterns = [
    path('', views.ArticleListCreate.as_view(), name='article_list_create')
]