from django.db import models
from django.conf import settings

class Conversation(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    message = models.TextField()
    bot_reply = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Conversation with {self.user.username} at {self.created_at}"

class ChatState(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE
    )
    current_step = models.CharField(max_length=50, default='start')  # 현재 대화 상태
    context_data = models.JSONField(default=dict)  # 대화 중 저장할 추가 정보

    def __str__(self):
        return f"{self.user.email} - {self.current_step}"

