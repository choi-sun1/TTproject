from rest_framework import serializers
from .models import Conversation, Message, Feedback, ChatState, Chatbot

class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = [
            'id', 'conversation', 'is_bot', 'content', 'created_at',
            'recommendation_type', 'recommendation_data'
        ]
        read_only_fields = ['created_at', 'conversation']

class ConversationSerializer(serializers.ModelSerializer):
    messages = MessageSerializer(many=True, read_only=True)
    last_message = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = ['id', 'user', 'title', 'created_at', 'updated_at', 'messages', 'last_message']
        read_only_fields = ['user', 'created_at', 'updated_at']

    def get_last_message(self, obj):
        last_message = obj.messages.last()
        if last_message:
            return MessageSerializer(last_message).data
        return None

class FeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feedback
        fields = ['id', 'message', 'user', 'is_helpful', 'comment', 'created_at']
        read_only_fields = ['user', 'created_at']

class ChatStateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatState
        fields = ['id', 'user', 'current_step', 'context_data', 'created_at', 'updated_at']
        read_only_fields = ['user', 'created_at', 'updated_at']

class ChatbotSerializer(serializers.ModelSerializer):
    class Meta:
        model = Chatbot
        fields = ['id', 'name', 'description', 'is_active', 'created_at']
        read_only_fields = ['created_at']
