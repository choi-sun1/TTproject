from django.urls import path, include
from . import views

urlpatterns = [
    path('chat/', views.chatbot_response, name='chatbot_response'),

]