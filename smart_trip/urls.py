from django.contrib import admin
from django.urls import path, include, re_path
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from . import views

schema_view = get_schema_view(
    openapi.Info(
        title="SmartTrip API",
        default_version='v1',
        description="""
        # SmartTrip API 문서
        
        ## 주요 기능
        1. 사용자 관리
           - 회원가입/로그인
           - 프로필 관리
           - JWT 인증
        
        2. 게시글
           - 여행 게시글 CRUD
           - 댓글
           - 좋아요
        
        3. 여행 일정
           - 일정 CRUD
           - 장소 검색 및 추가
           - 일정 공유
        
        4. AI 챗봇
           - 여행 일정 추천
           - 대화형 인터페이스
        
        ## 인증
        - API 요청시 Authorization 헤더에 JWT 토큰을 포함해야 합니다.
        - 형식: `Bearer <token>`
        """,
        terms_of_service="https://www.smarttrip.com/terms/",
        contact=openapi.Contact(email="support@smarttrip.com"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
    authentication_classes=[],
)

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Frontend routes
    path('', TemplateView.as_view(template_name='index.html'), name='home'),
    path('web/', include([
        path('accounts/', include('accounts.urls', namespace='accounts')),
        path('articles/', include('articles.urls', namespace='articles')),
        path('itineraries/', include('itineraries.urls', namespace='itineraries')),
        path('chatbot/', include('chatbot.urls', namespace='chatbot')),
    ])),
    
    # API URLs
    path('api/v1/', include([
        path('auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
        path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
        path('accounts/', include('accounts.urls', namespace='accounts_api')),
        path('articles/', include('articles.urls', namespace='articles_api')),
        path('itineraries/', include('itineraries.urls', namespace='itineraries_api')),
        path('chatbot/', include('chatbot.urls', namespace='chatbot_api')),
        path('test/', views.test_apps, name='test_apps'),
    ])),
    
    # Documentation
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns += [path('__debug__/', include('debug_toolbar.urls'))]
