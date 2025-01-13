from django.urls import path
from .views import ChatbotResponseView

urlpatterns = [
    path('chat/', ChatbotResponseView.as_view(), name='chatbot_response'),
]