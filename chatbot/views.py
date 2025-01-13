from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.http import JsonResponse
from .models import ChatState, Conversation
import re, openai

openai.api_key = 'your-openai-api-key' 
#환경변수나 설정파일에서 가져오는 방법 사용하기

class ChatbotResponseView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user  # 인증된 사용자
        user_message = request.data.get('message', '')

        # 대화 상태 확인
        chat_state, created = ChatState.objects.get_or_create(user=user)

        # 상태에 따른 로직 처리
        if chat_state.current_step == 'start':
            bot_reply = "여행 지역을 알려주세요."
            chat_state.current_step = 'get_location'

        elif chat_state.current_step == 'get_location':
            chat_state.context_data['location'] = user_message
            bot_reply = f"{user_message}에서 여행을 계획하시나요? 예산을 알려주세요."
            chat_state.current_step = 'get_budget'

        elif chat_state.current_step == 'get_budget':
            chat_state.context_data['budget'] = user_message
            bot_reply = f"예산이 {user_message}원이군요! 여행 기간을 알려주세요."
            chat_state.current_step = 'get_duration'

        elif chat_state.current_step == 'get_duration':
            # 여행 기간 입력 처리 (예: "2박 3일")
            duration_match = re.match(r"(\d+)박 (\d+)일", user_message)
            if duration_match:
                num_nights = int(duration_match.group(1))  # 2박
                num_days = int(duration_match.group(2))  # 3일
                chat_state.context_data['duration'] = {'nights': num_nights, 'days': num_days}
                bot_reply = f"{num_nights}박 {num_days}일 여행을 계획하셨군요! 추천 활동을 준비 중입니다."
                chat_state.current_step = 'get_activities'
            else:
                bot_reply = "여행 기간을 'X박 Y일' 형식으로 입력해주세요. 예: '2박 3일'"
            
        else:
            bot_reply = "감사합니다. 추천 결과를 정리하고 있어요!"
            chat_state.current_step = 'start'  # 대화 리셋

        # 대화 내용 Conversation 모델에 저장
        Conversation.objects.create(
            user=user,
            message=user_message,
            bot_reply=bot_reply
        )

        # 상태 저장
        chat_state.save()

        return JsonResponse({'bot_reply': bot_reply})