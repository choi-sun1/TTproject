from django.test import TestCase
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from django.contrib.auth import get_user_model
from .models import Conversation, Message, Feedback, ChatState

User = get_user_model()

class ChatbotTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123!',
            nickname='testuser'
        )
        self.client.force_authenticate(user=self.user)
        
        self.conversation = Conversation.objects.create(
            user=self.user,
            title='Test Conversation'
        )

    def test_start_conversation(self):
        """대화 시작 테스트"""
        url = reverse('chatbot:start-conversation')
        data = {'title': 'New Chat Session'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('conversation_id', response.data)
        self.assertEqual(response.data['title'], 'New Chat Session')

    def test_send_message(self):
        """메시지 전송 테스트"""
        url = reverse('chatbot:send-message')
        data = {
            'conversation_id': self.conversation.id,
            'content': '서울 여행 추천해줘',
            'is_bot': False
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        message = Message.objects.filter(conversation=self.conversation).first()
        self.assertIsNotNone(message)
        self.assertEqual(message.content, '서울 여행 추천해줘')

    def test_get_conversation_history(self):
        Message.objects.create(
            conversation=self.conversation,
            content='Test message',
            is_bot=False
        )
        url = reverse('chatbot:conversation-history', kwargs={'pk': self.conversation.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['messages']), 1)

    def test_provide_feedback(self):
        """피드백 제공 테스트"""
        message = Message.objects.create(
            conversation=self.conversation,
            content='Test message',
            is_bot=True
        )
        url = reverse('chatbot:provide-feedback', kwargs={'pk': message.pk})
        data = {
            'is_helpful': True,
            'comment': 'Very useful recommendation',
            'message': message.id  # message field 추가
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Feedback.objects.filter(message=message).exists())
