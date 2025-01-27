from django.conf import settings

def theme_settings(request):
    """
    테마 관련 설정을 템플릿에 전달하는 컨텍스트 프로세서
    """
    return {
        'THEME_SETTINGS': settings.THEME_SETTINGS,
        'current_theme': request.COOKIES.get(
            settings.THEME_SETTINGS['DARK_MODE_COOKIE_NAME'], 
            'light'
        )
    }
