from django.db import models
from django.contrib.auth.models import User
from django.conf import settings

class Conversation(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,  # 여기를 수정
        on_delete=models.CASCADE
    )
    user_message = models.TextField()  # 사용자가 입력한 메시지
    bot_reply = models.TextField()  # 챗봇 응답
    timestamp = models.DateTimeField(auto_now_add=True)  # 자동 생성되는 타임스탬프

    def __str__(self):
        return f"{self.user.username}: {self.user_message[:20]}"