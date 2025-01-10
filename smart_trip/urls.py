from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/accounts/', include('accounts.urls')),
    # 소셜 로그인
    path('api/accounts/', include('dj_rest_auth.urls')),
    path('api/accounts/', include('allauth.urls')),
    
    path('api/articles/', include('articles.urls')),
    path('api/chatbot/', include('chatbot.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
