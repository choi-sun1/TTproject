from django.http import JsonResponse

def test_apps(request):
    return JsonResponse({
        'accounts': 'ok',
        'articles': 'ok',
        'itineraries': 'ok',
        'chatbot': 'ok'
    })
