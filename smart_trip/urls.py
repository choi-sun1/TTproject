from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', TemplateView.as_view(template_name='home.html'), name='home'),
    path('accounts/', include('accounts.urls')),
    path('board/', include('board.urls')),
    path('chatbot/', include('chatbot.urls')),
    path('stays/', include('stays.urls')),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
