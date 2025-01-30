from django.urls import path
from . import views

urlpatterns = [
    path('chat/', views.ChatbotAPIView.as_view(), name='chatbot'),
    path('conversations/', views.ConversationHistoryAPIView.as_view(), name='conversation-history'),
    path('feedback/<int:message_id>/', views.FeedbackAPIView.as_view(), name='feedback'),
]
