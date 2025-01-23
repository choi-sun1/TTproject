from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

urlpatterns = [
    path('register/', views.RegisterAPIView.as_view(), name='api_register'),
    path('login/', views.LoginAPIView.as_view(), name='api_login'),
    path('profile/', views.UserProfileAPIView.as_view(), name='api_profile'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
