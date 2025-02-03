from django.urls import path
from . import views

app_name = 'chatbot'

urlpatterns = [
    path('chat/', views.ChatView.as_view(), name='chat'),
    path('new_chat/', views.NewChatView.as_view(), name='new_chat'),
]