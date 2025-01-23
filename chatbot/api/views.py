from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.conf import settings
import openai
from ..models import Conversation, Message, Feedback, ChatState
from ..serializers import ConversationSerializer, MessageSerializer
from ..services.gpt import generate_travel_recommendation

class ChatbotAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """챗봇 메시지 처리"""
        user_message = request.data.get('message')
        conversation_id = request.data.get('conversation_id')
        
        try:
            # 대화 컨텍스트 가져오기 또는 새로 생성
            if conversation_id:
                conversation = Conversation.objects.get(id=conversation_id)
            else:
                conversation = Conversation.objects.create(user=request.user)

            # 사용자 메시지 저장
            Message.objects.create(
                conversation=conversation,
                content=user_message,
                is_bot=False
            )

            # GPT API를 통한 응답 생성
            response_text = generate_travel_recommendation(user_message)

            # 봇 응답 저장
            bot_message = Message.objects.create(
                conversation=conversation,
                content=response_text,
                is_bot=True
            )

            return Response({
                'conversation_id': conversation.id,
                'message': MessageSerializer(bot_message).data
            })

        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class ConversationHistoryAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """사용자의 대화 기록 조회"""
        conversations = Conversation.objects.filter(user=request.user)
        serializer = ConversationSerializer(conversations, many=True)
        return Response(serializer.data)

class FeedbackAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, message_id):
        """챗봇 답변에 대한 피드백 제출"""
        try:
            feedback = Feedback.objects.create(
                message_id=message_id,
                user=request.user,
                is_helpful=request.data.get('is_helpful', True),
                comment=request.data.get('comment', '')
            )
            return Response({'message': '피드백이 성공적으로 저장되었습니다.'})
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
