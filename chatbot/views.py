from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.http import JsonResponse
from .models import ChatState, Conversation
import re, openai

openai.api_key = 'your-openai-api-key'
# 환경변수나 설정파일에서 API 키 가져오는 방법 사용하기

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
            # 여행 기간 입력 처리 (예: "2박 3일" 또는 "당일")
            duration_match = re.match(r"(\d+)박 (\d+)일", user_message)
            if duration_match:
                num_nights = int(duration_match.group(1))  # 2박
                num_days = int(duration_match.group(2))  # 3일
                chat_state.context_data['duration'] = {'nights': num_nights, 'days': num_days}

                # 당일여행 여부 확인
                if num_nights == 0:
                    bot_reply = f"{num_days}일 동안의 당일 여행을 계획하셨군요! 추천 활동을 준비 중입니다."
                    chat_state.current_step = 'get_activities'  # 숙박 질문 건너뛰기
                else:
                    bot_reply = f"{num_nights}박 {num_days}일 여행을 계획하셨군요! 숙박 조건을 알려주세요."
                    chat_state.current_step = 'get_accommodation'
            else:
                bot_reply = "여행 기간을 'X박 Y일' 형식으로 입력해주세요. 예: '2박 3일' 또는 '당일'"

        elif chat_state.current_step == 'get_accommodation':
            # 숙박 조건 입력 받기
            chat_state.context_data['accommodation'] = user_message
            bot_reply = "숙박 조건을 저장했습니다. 추천 활동을 준비 중입니다."
            chat_state.current_step = 'get_activities'

        elif chat_state.current_step == 'get_activities':
            # LLM 또는 RAG 기반 추천 로직 추가
            bot_reply = "추천 활동 리스트를 준비 중이에요! 잠시만 기다려주세요."
            chat_state.current_step = 'start'  # 대화 리셋

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

from rest_framework import generics, permissions, status
from rest_framework.response import Response
from .models import Conversation, Message, Feedback
from .serializers import ConversationSerializer, MessageSerializer, FeedbackSerializer
from django.shortcuts import get_object_or_404

class StartConversationView(generics.CreateAPIView):
    serializer_class = ConversationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        conversation = serializer.save(user=request.user)
        return Response({
            'conversation_id': conversation.id,
            'title': conversation.title,
            'message': 'Conversation started successfully'
        }, status=status.HTTP_201_CREATED)

class SendMessageView(generics.CreateAPIView):
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        conversation_id = request.data.get('conversation_id')
        if not conversation_id:
            return Response(
                {'error': 'conversation_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        conversation = get_object_or_404(
            Conversation,
            id=conversation_id,
            user=request.user
        )
        
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(conversation=conversation)
        
        return Response(serializer.data, status=status.HTTP_200_OK)

class ConversationHistoryView(generics.RetrieveAPIView):
    serializer_class = ConversationSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Conversation.objects.all()

class ProvideFeedbackView(generics.CreateAPIView):
    serializer_class = FeedbackSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        message_id = self.kwargs.get('pk')
        message = get_object_or_404(Message, id=message_id)
        serializer.save(user=self.request.user, message=message)

from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin

class ChatbotView(LoginRequiredMixin, TemplateView):
    template_name = 'chatbot/chat.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['KAKAO_MAPS_API_KEY'] = self.request.COOKIES.get('KAKAO_MAPS_API_KEY', '')
        return context
