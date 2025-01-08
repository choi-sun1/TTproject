from django.urls import path, include
from . import views

app_name = 'accounts'

urlpatterns = [
    path('signup/', views.SignupView.as_view(), name='signup'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('<str:username>/', views.UserProfileView.as_view(), name='profile'),
    path('<str:username>/delete/', views.UserDeleteView.as_view(), name='delete'),
]