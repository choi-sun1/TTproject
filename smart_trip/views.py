from django.shortcuts import redirect
from django.http import JsonResponse

def test_apps(request):
    return JsonResponse({
        'accounts': 'ok',
        'articles': 'ok',
        'itineraries': 'ok',
        'chatbot': 'ok'
    })

def signup_view(request):
    """회원가입 페이지로 리다이렉트"""
    return redirect('accounts_web:signup')
