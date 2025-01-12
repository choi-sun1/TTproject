from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from .models import Conversation, ChatState

class ChatbotResponseView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        user_message = request.data.get('message', '')
        
        # 대화 상태 확인/생성
        chat_state, created = ChatState.objects.get_or_create(user=user)
        current_step = chat_state.current_step
        collected_data = chat_state.data

        # 단계별 처리
        if current_step == "start":
            chat_state.current_step = "location"
            chat_state.save()
            return JsonResponse({"bot_reply": "여행 지역을 알려주세요."})

        elif current_step == "location":
            collected_data["location"] = user_message
            chat_state.current_step = "budget"
            chat_state.save()
            return JsonResponse({"bot_reply": "여행 예산은 어느 정도인가요?"})

        elif current_step == "budget":
            collected_data["budget"] = user_message
            chat_state.current_step = "activity"
            chat_state.save()
            return JsonResponse({"bot_reply": "관심 있는 활동(예: 맛집, 쇼핑, 자연경관)은 무엇인가요?"})

        elif current_step == "activity":
            collected_data["activity"] = user_message
            chat_state.current_step = "recommend"
            chat_state.save()
            # 외부 API를 사용하여 추천 데이터 생성
            recommendations = self.get_recommendations(collected_data)
            return JsonResponse({"bot_reply": recommendations})

        else:
            return JsonResponse({"bot_reply": "대화가 완료되었습니다. 새로운 여행 계획을 시작하시려면 '새로 시작'이라고 입력해주세요."})

    def get_recommendations(self, data):
        # 추천 로직 또는 API 호출
        location = data.get("location")
        budget = data.get("budget")
        activity = data.get("activity")

        # 예시: Mock 추천 데이터
        return f"{location}에서 {budget} 예산으로 {activity}를 즐길 수 있는 장소를 추천드릴게요!"