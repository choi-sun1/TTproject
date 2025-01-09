from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/accounts/', include('accounts.urls')),
    path('api/articles/', include('articles.urls')),
    path('api/chatbot/', include('chatbot.urls')),
    path('chatbot/', include('chatbot.urls')),
    #path('api/accounts/token/', include('rest_framework_simplejwt.urls')),
    
    # JWT 관련 URL 직접 추가
    path('api/accounts/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/accounts/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/accounts/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
