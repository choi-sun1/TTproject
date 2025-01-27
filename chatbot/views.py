from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.conf import settings
from openai import OpenAI
from .models import Conversation
from .forms import ChatForm

CLIENT = OpenAI(api_key=settings.OPENAI_API_KEY)

@login_required
def chat_view(request):
    if request.method == 'GET':
        return render(request, 'chatbot/chat.html')

    completion = None
    prompt = '''
    너는 여행 계획을 돕는 챗봇이야.
    국내 여행만을 대상으로 도와줄 수 있어.'''
    
    if request.method == 'POST':
        user = request.user
        form = ChatForm(request.POST)
        if form.is_valid():
            user_message = form.cleaned_data["user_message"]

            # OpenAI API 호출
            completion = CLIENT.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": user_message}
                ]
            )
            bot_reply = completion.choices[0].message.content
        
            # 새로운 메시지만 저장
            conversation = Conversation.objects.create(
                user=user,
                user_message=user_message,
                bot_reply=bot_reply
            )

            # 새로운 메시지만 반환 (이전 대화 불러오지 않음)
            return render(request, 'chatbot/chat.html', {
                'form': form,
                'new_message': conversation  # 새 메시지만 전달
            })

    return render(request, 'chatbot/chat.html', {'form': ChatForm()})

from django.shortcuts import redirect

@login_required
def new_chat(request):
    # 현재 사용자의 대화 기록 삭제
    Conversation.objects.filter(user=request.user).delete()
    return redirect('chatbot:chat')  # chat_view로 리디렉션