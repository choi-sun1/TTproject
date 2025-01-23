from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from . import views

app_name = 'accounts_api'

urlpatterns = [
    path('register/', views.RegisterAPIView.as_view(), name='register'),
    path('login/', views.LoginAPIView.as_view(), name='login'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('profile/', views.ProfileAPIView.as_view(), name='profile'),
    path('profile/update/', views.ProfileUpdateAPIView.as_view(), name='profile_update'),
    path('users/<str:nickname>/', views.UserProfileDetailAPIView.as_view(), name='user_detail'),
]
