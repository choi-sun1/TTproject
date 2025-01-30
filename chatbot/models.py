from django.db import models
from django.conf import settings

class Conversation(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='conversations'
    )
    user_message = models.TextField()
    bot_reply = models.TextField()  # 필수 필드로 설정됨
    timestamp = models.DateTimeField(auto_now_add=True)  # created_at에서 timestamp로 변경

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.user.username} - {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}"