from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'accounts'  # accounts_web에서 accounts로 변경

urlpatterns = [
    # Frontend routes only
    path('signup/', views.SignupView.as_view(), name='signup'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.profile_edit, name='profile_edit'),
    path('profile/<str:nickname>/', views.UserProfileView.as_view(), name='user_profile'),
]