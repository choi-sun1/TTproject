from django.db import models

class User(models.Model):
    username = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    date_joined = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.username


class Conversation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='conversations')
    message = models.TextField()  # 사용자가 입력한 메시지
    bot_reply = models.TextField()  # 챗봇의 답변
    timestamp = models.DateTimeField(auto_now_add=True)  # 대화 시간

    def __str__(self):
        return f"Conversation with {self.user.username} at {self.timestamp}"


class FAQ(models.Model):
    question = models.CharField(max_length=255)
    answer = models.TextField()

    def __str__(self):
        return self.question
