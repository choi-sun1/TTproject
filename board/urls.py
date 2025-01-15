from django.urls import path
from . import views

app_name = 'board'

urlpatterns = [
    path('', views.post_list, name='list'),
    path('<int:pk>/', views.post_detail, name='detail'),
    path('write/', views.post_write, name='write'),
    path('<int:pk>/edit/', views.post_edit, name='edit'),
    path('<int:pk>/delete/', views.post_delete, name='delete'),
    path('<int:post_id>/comment/', views.comment_create, name='comment_create'),
    path('<int:pk>/like/', views.post_like, name='like'),
]
