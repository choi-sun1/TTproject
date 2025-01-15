from django.urls import path
from .views import chat_view

app_name = 'chatbot'

urlpatterns = [
    path('', chat_view, name='chat'),
]