from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.conf import settings
from openai import OpenAI
from .models import Conversation
from .forms import ChatForm

CLIENT = OpenAI(api_key=settings.OPENAI_API_KEY)

@login_required
def chat_view(request):
    if request.method == 'GET':
        # 새로운 대화 플래그 확인
        show_history = request.GET.get('show_history', 'false') == 'true'
        if show_history:
            conversations = Conversation.objects.filter(user=request.user).order_by('timestamp')
        else:
            conversations = []

        return render(request, 'chatbot/chat.html', {'conversations': conversations, 'form': ChatForm(), 'show_history': show_history})

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
                'new_message': conversation,  # 새 메시지만 전달
                'conversations': Conversation.objects.filter(user=request.user).order_by('timestamp')
            })

    return render(request, 'chatbot/chat.html', {'form': ChatForm()})

@login_required
def new_chat(request):
    # 새로운 대화를 시작할 때 기존 대화 내역을 숨기기 위해 플래그 설정
    request.session['new_chat'] = True
    return redirect('chatbot:chat')  # chat_view로 리디렉션