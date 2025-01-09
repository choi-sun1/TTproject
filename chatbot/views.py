import requests
from django.conf import settings
from django.http import JsonResponse
from .models import FAQ, Conversation

def chatbot_response(request):
    # 클라이언트에서 전달된 JWT 토큰을 Authorization 헤더에서 가져옵니다.
    token = request.headers.get('Authorization')

    if token and token.startswith('Bearer '):
        token = token[7:]  # 'Bearer ' 부분을 제외한 토큰만 사용
    else:
        return JsonResponse({'error': '로그인 후 이용해주세요.'}, status=403)

    # JWT 토큰 검증을 위한 API 요청
    try:
        response = requests.post(
            f'{settings.BASE_URL}/accounts/token/verify/',  # accounts 앱의 JWT 토큰 검증 URL
            json={'token': token}  # JSON 형식으로 전달
        )

        if response.status_code != 200:
            return JsonResponse({'error': '유효하지 않은 토큰입니다.'}, status=403)

    except requests.exceptions.RequestException as e:
        return JsonResponse({'error': '토큰 검증 중 오류가 발생했습니다.'}, status=500)

    # 토큰이 유효하다면, 사용자 메시지 처리
    user_message = request.GET.get('message', '')

    # FAQ에서 답변을 찾기
    faq = FAQ.objects.filter(question__icontains=user_message).first()
    bot_reply = faq.answer if faq else "저는 아직 그걸 알지 못해요."

    # 대화 기록 저장
    conversation = Conversation.obje
