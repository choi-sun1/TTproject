from django.urls import path
from . import views

app_name = 'chatbot'

urlpatterns = [
    path('start/', views.StartConversationView.as_view(), name='start-conversation'),
    path('send/', views.SendMessageView.as_view(), name='send-message'),
    path('conversations/<int:pk>/', views.ConversationHistoryView.as_view(), name='conversation-history'),
    path('feedback/<int:pk>/', views.ProvideFeedbackView.as_view(), name='provide-feedback'),
]